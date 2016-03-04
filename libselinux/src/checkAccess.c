/*-*- Mode: C; c-basic-offset: 8; indent-tabs-mode: nil -*-*/
#include <unistd.h>
#include <sys/types.h>
#include <stdlib.h>
#include <errno.h>
#include "selinux_internal.h"
#include <selinux/avc.h>
#include "avc_internal.h"

static pthread_once_t once = PTHREAD_ONCE_INIT;
static int selinux_enabled;

static int avc_reset_callback(uint32_t event __attribute__((unused)),
		      security_id_t ssid __attribute__((unused)),
		      security_id_t tsid __attribute__((unused)),
		      security_class_t tclass __attribute__((unused)),
		      access_vector_t perms __attribute__((unused)),
		      access_vector_t *out_retained __attribute__((unused)))
{
	flush_class_cache();
	return 0;
}

static void avc_init_once(void)
{
	selinux_enabled = is_selinux_enabled();
	if (selinux_enabled == 1) {
		if (avc_open(NULL, 0))
			return;
		avc_add_callback(avc_reset_callback, AVC_CALLBACK_RESET,
				 0, 0, 0, 0);
	}
}

int selinux_check_access_raw(const char *scon, const char *tcon, const char *class, const char *perm, void *aux) {
	int rc;
	security_id_t scon_id;
	security_id_t tcon_id;
	security_class_t sclass;
	access_vector_t av;

	__selinux_once(once, avc_init_once);

	if (selinux_enabled != 1)
		return 0;

	rc = avc_context_to_sid_raw(scon, &scon_id);
	if (rc < 0)
		return rc;

	rc = avc_context_to_sid_raw(tcon, &tcon_id);
	if (rc < 0)
		return rc;

	(void) avc_netlink_check_nb();

	sclass = string_to_security_class(class);
	if (sclass == 0) {
	        rc = errno;
	        avc_log(SELINUX_ERROR, "Unknown class %s", class);
	        if (security_deny_unknown() == 0)
		       return 0;
	        errno = rc;
	        return -1;
	}

	av = string_to_av_perm(sclass, perm);
	if (av == 0) {
	        rc = errno;
	        avc_log(SELINUX_ERROR, "Unknown permission %s for class %s", perm, class);
	        if (security_deny_unknown() == 0)
		       return 0;
	        errno = rc;
	        return -1;
	}

	return avc_has_perm (scon_id, tcon_id, sclass, av, NULL, aux);
}


int selinux_check_access(const char *scon, const char *tcon, const char *class, const char *perm, void *aux) {
	int rc;
	char * scon_raw, * tcon_raw;

	__selinux_once(once, avc_init_once);

	if (selinux_enabled != 1)
		return 0;

	rc  = selinux_trans_to_raw_context(scon, &scon_raw);
	if (rc < 0)
		return rc;

	rc  = selinux_trans_to_raw_context(tcon, &tcon_raw);
	if (rc < 0) {
		freecon(scon_raw);
		return rc;
	}

	rc = selinux_check_access_raw(scon_raw, tcon_raw, class, perm, aux);

	freecon(scon_raw);
	freecon(tcon_raw);
	return rc;
}


int selinux_check_passwd_access(access_vector_t requested)
{
	int status = -1;
	char *user_context;
	if (is_selinux_enabled() == 0)
		return 0;
	if (getprevcon_raw(&user_context) == 0) {
		security_class_t passwd_class;
		struct av_decision avd;
		int retval;

		passwd_class = string_to_security_class("passwd");
		if (passwd_class == 0)
			return 0;

		retval = security_compute_av_raw(user_context,
						     user_context,
						     passwd_class,
						     requested,
						     &avd);

		if ((retval == 0) && ((requested & avd.allowed) == requested)) {
			status = 0;
		}
		freecon(user_context);
	}

	if (status != 0 && security_getenforce() == 0)
		status = 0;

	return status;
}

hidden_def(selinux_check_passwd_access)

int checkPasswdAccess(access_vector_t requested)
{
	return selinux_check_passwd_access(requested);
}
