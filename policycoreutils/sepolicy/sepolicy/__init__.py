#!/usr/bin/python

# Author: Dan Walsh <dwalsh@redhat.com>
# Author: Ryan Hallisey <rhallise@redhat.com>

# import _policy
import setools
import selinux
import glob
PROGNAME = "policycoreutils"
import gettext
import sepolgen.defaults as defaults
import sepolgen.interfaces as interfaces
import sys
gettext.bindtextdomain(PROGNAME, "/usr/share/locale")
gettext.textdomain(PROGNAME)
try:
    gettext.install(PROGNAME,
                    localedir="/usr/share/locale",
                    unicode=False,
                    codeset='utf-8')
except IOError:
    import __builtin__
    __builtin__.__dict__['_'] = unicode

TYPE = setools.TypeQuery
ROLE = setools.RoleQuery
ATTRIBUTE = setools.TypeAttributeQuery
PORT = setools.PortconQuery
USER = setools.UserQuery
BOOLEAN = setools.BoolQuery
TCLASS = setools.ObjClassQuery
ROLE_ALLOW = setools.RBACRuleQuery
TYPE_ALLOW = setools.TERuleQuery
# SENS = 'sens'
# CATS = 'cats'

ALLOW = 'allow'
AUDITALLOW = 'auditallow'
NEVERALLOW = 'neverallow'
DONTAUDIT = 'dontaudit'
SOURCE = 'source'
TARGET = 'target'
PERMS = 'perms'
CLASS = 'tclass'
TRANSITION = 'type_transition'


def info(setype, **kwargs):
    # dict_list = _policy.info(setype, name)
    # policy = setools.SELinuxPolicy()
    return list(setype(selinuxpolicy, **kwargs).results())
    # return dict_list


def search(types, info={}):
    seinfo = info
    valid_types = [ALLOW, AUDITALLOW, NEVERALLOW, DONTAUDIT, TRANSITION]
    for setype in types:
        if setype not in valid_types:
            raise ValueError("Type has to be in %s" % valid_types)
        seinfo[setype] = True

    perms = []
    if PERMS in seinfo:
        perms = info[PERMS]
        seinfo[PERMS] = ",".join(seinfo[PERMS])

    dict_list = _policy.search(seinfo)
    if dict_list and len(perms) != 0:
        dict_list = filter(lambda x: _dict_has_perms(x, perms), dict_list)
    return dict_list


def get_conditionals(src, dest, tclass, perm):
    tdict = {}
    tlist = []
    if dest.endswith("_t"):
        allows = search([ALLOW], {SOURCE: src, TARGET: dest, CLASS: tclass, PERMS: perm})
    else:
        # to include attribute
        allows = search([ALLOW], {SOURCE: src, CLASS: tclass, PERMS: perm})
        for i in allows:
            if i['target'] == dest:
                allows = []
                allows.append(i)
    try:
        for i in map(lambda y: (y), filter(lambda x: set(perm).issubset(x[PERMS]) and x['boolean'], allows)):
            tdict.update({'source': i['source'], 'boolean': i['boolean']})
            if tdict not in tlist:
                tlist.append(tdict)
                tdict = {}
    except KeyError:
        return(tlist)

    return (tlist)


def get_conditionals_format_text(cond):
    enabled = len(filter(lambda x: x['boolean'][0][1], cond)) > 0
    return _("-- Allowed %s [ %s ]") % (enabled, " || ".join(set(map(lambda x: "%s=%d" % (x['boolean'][0][0], x['boolean'][0][1]), cond))))


def get_types_from_attribute(attribute):
    return info(ATTRIBUTE, attribute)[0]["types"]

file_type_str = {}
file_type_str["a"] = _("all files")
file_type_str["f"] = _("regular file")
file_type_str["d"] = _("directory")
file_type_str["c"] = _("character device")
file_type_str["b"] = _("block device")
file_type_str["s"] = _("socket file")
file_type_str["l"] = _("symbolic link")
file_type_str["p"] = _("named pipe")

trans_file_type_str = {}
trans_file_type_str[""] = "a"
trans_file_type_str["--"] = "f"
trans_file_type_str["-d"] = "d"
trans_file_type_str["-c"] = "c"
trans_file_type_str["-b"] = "b"
trans_file_type_str["-s"] = "s"
trans_file_type_str["-l"] = "l"
trans_file_type_str["-p"] = "p"


def get_file_types(setype):
    flist = []
    mpaths = {}
    for f in get_all_file_types():
        if f.startswith(gen_short_name(setype)):
            flist.append(f)
    fcdict = get_fcdict()
    for f in flist:
        try:
            mpaths[f] = (fcdict[f]["regex"], file_type_str[fcdict[f]["ftype"]])
        except KeyError:
            mpaths[f] = []
    return mpaths


def get_writable_files(setype):
    all_attributes = get_all_attributes()
    file_types = get_all_file_types()
    all_writes = []
    mpaths = {}
    permlist = search([ALLOW], {'source': setype, 'permlist': ['open', 'write'], 'class': 'file'})
    if permlist == None or len(permlist) == 0:
        return mpaths

    fcdict = get_fcdict()

    attributes = ["proc_type", "sysctl_type"]
    for i in permlist:
        if i['target'] in attributes:
            continue
        if "enabled" in i:
            if not i["enabled"]:
                continue
        if i['target'].endswith("_t"):
            if i['target'] not in file_types:
                continue
            if i['target'] not in all_writes:
                if i['target'] != setype:
                    all_writes.append(i['target'])
        else:
            for t in get_types_from_attribute(i['target']):
                if t not in all_writes:
                    all_writes.append(t)

    for f in all_writes:
        try:
            mpaths[f] = (fcdict[f]["regex"], file_type_str[fcdict[f]["ftype"]])
        except KeyError:
            mpaths[f] = []  # {"regex":[],"paths":[]}
    return mpaths

import os
import re
import sys


def find_file(reg):
    if os.path.exists(reg):
        return [reg]
    try:
        pat = re.compile(r"%s$" % reg)
    except:
        print "bad reg:", reg
        return []
    p = reg
    if p.endswith("(/.*)?"):
        p = p[:-6] + "/"

    path = os.path.dirname(p)

    try:                       # Bug fix: when "all files on system"
        if path[-1] != "/":    # is pass in it breaks without try block
            path += "/"
    except IndexError:
        print "try failed got an IndexError"
        pass

    try:
        pat = re.compile(r"%s$" % reg)
        return filter(pat.match, map(lambda x: path + x, os.listdir(path)))
    except:
        return []


def find_all_files(domain, exclude_list=[]):
    all_entrypoints = []
    executable_files = get_entrypoints(domain)
    for exe in executable_files.keys():
        if exe.endswith("_exec_t") and exe not in exclude_list:
            for path in executable_files[exe]:
                for f in find_file(path):
                    return f
                    #all_entrypoints.append(f)
    return None

#return all_entrypoints


def find_entrypoint_path(exe, exclude_list=[]):
    fcdict = get_fcdict()
    try:
        if exe.endswith("_exec_t") and exe not in exclude_list:
            for path in fcdict[exe]["regex"]:
                for f in find_file(path):
                    return f
    except KeyError:
        pass
    return None


def read_file_equiv(edict, fc_path, modify):
    fd = open(fc_path, "r")
    fc = fd.readlines()
    fd.close()
    for e in fc:
        f = e.split()
        edict[f[0]] = {"equiv": f[1], "modify": modify}
    return edict

file_equiv_modified = None


def get_file_equiv_modified(fc_path=selinux.selinux_file_context_path()):
    global file_equiv_modified
    if file_equiv_modified:
        return file_equiv_modified
    file_equiv_modified = {}
    file_equiv_modified = read_file_equiv(file_equiv_modified, fc_path + ".subs", modify=True)
    return file_equiv_modified

file_equiv = None


def get_file_equiv(fc_path=selinux.selinux_file_context_path()):
    global file_equiv
    if file_equiv:
        return file_equiv
    file_equiv = get_file_equiv_modified(fc_path)
    file_equiv = read_file_equiv(file_equiv, fc_path + ".subs_dist", modify=False)
    return file_equiv

local_files = None


def get_local_file_paths(fc_path=selinux.selinux_file_context_path()):
    global local_files
    if local_files:
        return local_files
    local_files = []
    fd = open(fc_path + ".local", "r")
    fc = fd.readlines()
    fd.close()
    for i in fc:
        rec = i.split()
        if len(rec) == 0:
            continue
        try:
            if len(rec) > 2:
                ftype = trans_file_type_str[rec[1]]
            else:
                ftype = "a"

            local_files.append((rec[0], ftype))
        except KeyError:
            pass
    return local_files

fcdict = None


def get_fcdict(fc_path=selinux.selinux_file_context_path()):
    global fcdict
    if fcdict:
        return fcdict
    fd = open(fc_path, "r")
    fc = fd.readlines()
    fd.close()
    fd = open(fc_path + ".homedirs", "r")
    fc += fd.readlines()
    fd.close()
    fcdict = {}
    fd = open(fc_path + ".local", "r")
    fc += fd.readlines()
    fd.close()

    for i in fc:
        rec = i.split()
        try:
            if len(rec) > 2:
                ftype = trans_file_type_str[rec[1]]
            else:
                ftype = "a"

            t = rec[-1].split(":")[2]
            if t in fcdict:
                fcdict[t]["regex"].append(rec[0])
            else:
                fcdict[t] = {"regex": [rec[0]], "ftype": ftype}
        except:
            pass

    fcdict["logfile"] = {"regex": ["all log files"]}
    fcdict["user_tmp_type"] = {"regex": ["all user tmp files"]}
    fcdict["user_home_type"] = {"regex": ["all user home files"]}
    fcdict["virt_image_type"] = {"regex": ["all virtual image files"]}
    fcdict["noxattrfs"] = {"regex": ["all files on file systems which do not support extended attributes"]}
    fcdict["sandbox_tmpfs_type"] = {"regex": ["all sandbox content in tmpfs file systems"]}
    fcdict["user_tmpfs_type"] = {"regex": ["all user content in tmpfs file systems"]}
    fcdict["file_type"] = {"regex": ["all files on the system"]}
    fcdict["samba_share_t"] = {"regex": ["use this label for random content that will be shared using samba"]}
    return fcdict


def get_transitions_into(setype):
    try:
        return filter(lambda x: x["transtype"] == setype, search([TRANSITION], {'class': 'process'}))
    except TypeError:
        pass
    return None


def get_transitions(setype):
    try:
        return search([TRANSITION], {'source': setype, 'class': 'process'})
    except TypeError:
        pass
    return None


def get_file_transitions(setype):
    try:
        return filter(lambda x: x['class'] != "process", search([TRANSITION], {'source': setype}))
    except TypeError:
        pass
    return None


def get_boolean_rules(setype, boolean):
    boollist = []
    permlist = search([ALLOW], {'source': setype})
    for p in permlist:
        if "boolean" in p:
            try:
                for b in p["boolean"]:
                    if boolean in b:
                        boollist.append(p)
            except:
                pass
    return boollist


def get_all_entrypoints():
    return get_types_from_attribute("entry_type")


def get_entrypoint_types(setype):
    entrypoints = []
    try:
        entrypoints = map(lambda x: x['target'], filter(lambda x: x['source'] == setype, search([ALLOW], {'source': setype, 'permlist': ['entrypoint'], 'class': 'file'})))
    except TypeError:
        pass
    return entrypoints


def get_init_transtype(path):
    entrypoint = selinux.getfilecon(path)[1].split(":")[2]
    try:
        entrypoints = filter(lambda x: x['target'] == entrypoint, search([TRANSITION], {'source': "init_t", 'class': 'process'}))
        if len(entrypoints) == 0:
            return None
        return entrypoints[0]["transtype"]
    except TypeError:
        pass
    return None


def get_init_entrypoint(transtype):
    try:
        entrypoints = filter(lambda x: x['transtype'] == transtype, search([TRANSITION], {'source': "init_t", 'class': 'process'}))
        if len(entrypoints) == 0:
            return None
        return entrypoints[0]["target"]
    except TypeError:
        pass
    return None


def get_init_entrypoint_target(entrypoint):
    try:
        entrypoints = map(lambda x: x['transtype'], search([TRANSITION], {'source': "init_t", 'target': entrypoint, 'class': 'process'}))
        return entrypoints[0]
    except TypeError:
        pass
    return None


def get_entrypoints(setype):
    fcdict = get_fcdict()
    mpaths = {}
    for f in get_entrypoint_types(setype):
        try:
            mpaths[f] = (fcdict[f]["regex"], file_type_str[fcdict[f]["ftype"]])
        except KeyError:
            mpaths[f] = []
    return mpaths


def get_installed_policy(root="/"):
    try:
        path = root + selinux.selinux_binary_policy_path()
        policies = glob.glob("%s.*" % path)
        policies.sort()
        return policies[-1]
    except:
        pass
    raise ValueError(_("No SELinux Policy installed"))

methods = []


def get_methods():
    global methods
    if len(methods) > 0:
        return methods
    gen_interfaces()
    fn = defaults.interface_info()
    try:
        fd = open(fn)
    # List of per_role_template interfaces
        ifs = interfaces.InterfaceSet()
        ifs.from_file(fd)
        methods = ifs.interfaces.keys()
        fd.close()
    except:
        sys.stderr.write("could not open interface info [%s]\n" % fn)
        sys.exit(1)

    methods.sort()
    return methods

all_types = None


def get_all_types():
    global all_types
    if all_types == None:
        all_types = [str(x) for x in info(TYPE)]
    return all_types

user_types = None


def get_user_types():
    global user_types
    if user_types == None:
        user_types = [str(x) for x in info(TYPE, attrs=["userdomain"])]
    return user_types

role_allows = None


def get_all_role_allows():
    global role_allows
    if role_allows:
        return role_allows
    role_allows = {}
    for r in info(ROLE_ALLOW, ruletype=["allow"]):
        if r.source == "system_r" or r.target == "system_r":
            continue
        if str(r.source) in role_allows:
            role_allows[str(r.source)].append(str(r.target))
        else:
            role_allows[str(r.source)] = [str(r.target)]

    return role_allows


def get_all_entrypoint_domains():
    import re
    all_domains = []
    types = get_all_types()
    types.sort()
    for i in types:
        m = re.findall("(.*)%s" % "_exec_t$", i)
        if len(m) > 0:
            if len(re.findall("(.*)%s" % "_initrc$", m[0])) == 0 and m[0] not in all_domains:
                all_domains.append(m[0])
    return all_domains

portrecs = None
portrecsbynum = None


def gen_interfaces():
    import commands
    ifile = defaults.interface_info()
    headers = defaults.headers()
    rebuild = False
    try:
        if os.stat(headers).st_mtime <= os.stat(ifile).st_mtime:
            return
    except OSError:
        pass

    if os.getuid() != 0:
        raise ValueError(_("You must regenerate interface info by running /usr/bin/sepolgen-ifgen"))
    print commands.getstatusoutput("/usr/bin/sepolgen-ifgen")[1]


def gen_port_dict():
    global portrecs
    global portrecsbynum
    if portrecs:
        return (portrecs, portrecsbynum)
    portrecsbynum = {}
    portrecs = {}
    for i in info(PORT):
        if i.ports.low == i.ports.high:
            port = str(i.ports.low)
        else:
            port = "%s-%s" % (i.ports.low, i.ports.high)

        if (str(i.context.type_), i._proto_to_text[i.protocol]) in portrecs:
            portrecs[(str(i.context.type_), i._proto_to_text[i.protocol])].append(port)
        else:
            portrecs[(str(i.context.type_), i._proto_to_text[i.protocol])] = [port]

        portrecsbynum[(i.ports.low, i.ports.high, i._proto_to_text[i.protocol])] = (str(i.context.type_), str(i.context.range_))

    return (portrecs, portrecsbynum)

all_domains = None


def get_all_domains():
    global all_domains
    if not all_domains:
        all_domains = [str(x) for x in info(TYPE, attrs=["domain"])]
    return all_domains

roles = None


def get_all_roles():
    global roles
    if roles:
        return roles
    roles = [str(x) for x in info(ROLE)]
    try:
        roles.remove("object_r")
    except:
        pass
    roles.sort()
    return roles

selinux_user_list = None


def get_selinux_users():
    global selinux_user_list
    if not selinux_user_list:
        selinux_user_list = []
        for x in info(USER):
            selinux_user_list.append({
                    'name': str(x),
                    'roles': [str(y) for y in x.roles],
                    'level': str(x.mls_level),
                    'range': "".join(str(x.mls_range).split(" "))
            })
    return selinux_user_list

login_mappings = None


def get_login_mappings():
    global login_mappings
    if login_mappings:
        return login_mappings

    fd = open(selinux.selinux_usersconf_path(), "r")
    buf = fd.read()
    fd.close()
    login_mappings = []
    for b in buf.split("\n"):
        b = b.strip()
        if len(b) == 0 or b.startswith("#"):
            continue
        x = b.split(":")
        login_mappings.append({"name": x[0], "seuser": x[1], "mls": ":".join(x[2:])})
    return login_mappings


def get_all_users():
    users = map(lambda x: x['name'], get_selinux_users())
    users.sort()
    return users

file_types = None


def get_all_file_types():
    global file_types
    if file_types:
        return file_types
    file_types = [x.__str__() for x in info(TYPE, attrs=["file_type"])]
    file_types.sort()
    return file_types

port_types = None


def get_all_port_types():
    global port_types
    if port_types:
        return port_types
    port_types = [x.__str__() for x in info(TYPE, attrs=["port_type"])]
    port_types.sort()
    return port_types

bools = None


def get_all_bools():
    global bools
    if not bools:
        bools = [x.__str__() for x in info(BOOLEAN)]
        bools.sort()
    return bools


def prettyprint(f, trim):
    return " ".join(f[:-len(trim)].split("_"))


def markup(f):
    return f

# Autofill for adding files *************************
DEFAULT_DIRS = {}
DEFAULT_DIRS["/etc"] = "etc_t"
DEFAULT_DIRS["/tmp"] = "tmp_t"
DEFAULT_DIRS["/usr/lib/systemd/system"] = "unit_file_t"
DEFAULT_DIRS["/lib/systemd/system"] = "unit_file_t"
DEFAULT_DIRS["/etc/systemd/system"] = "unit_file_t"
DEFAULT_DIRS["/var/cache"] = "var_cache_t"
DEFAULT_DIRS["/var/lib"] = "var_lib_t"
DEFAULT_DIRS["/var/log"] = "log_t"
DEFAULT_DIRS["/var/run"] = "var_run_t"
DEFAULT_DIRS["/run"] = "var_run_t"
DEFAULT_DIRS["/run/lock"] = "var_lock_t"
DEFAULT_DIRS["/var/run/lock"] = "var_lock_t"
DEFAULT_DIRS["/var/spool"] = "var_spool_t"
DEFAULT_DIRS["/var/www"] = "content_t"


def get_description(f, markup=markup):

    txt = "Set files with the %s type, if you want to " % markup(f)

    if f.endswith("_var_run_t"):
        return txt + "store the %s files under the /run or /var/run directory." % prettyprint(f, "_var_run_t")
    if f.endswith("_pid_t"):
        return txt + "store the %s files under the /run directory." % prettyprint(f, "_pid_t")
    if f.endswith("_var_lib_t"):
        return txt + "store the %s files under the /var/lib directory." % prettyprint(f, "_var_lib_t")
    if f.endswith("_var_t"):
        return txt + "store the %s files under the /var directory." % prettyprint(f, "_var_lib_t")
    if f.endswith("_var_spool_t"):
        return txt + "store the %s files under the /var/spool directory." % prettyprint(f, "_spool_t")
    if f.endswith("_spool_t"):
        return txt + "store the %s files under the /var/spool directory." % prettyprint(f, "_spool_t")
    if f.endswith("_cache_t") or f.endswith("_var_cache_t"):
        return txt + "store the files under the /var/cache directory."
    if f.endswith("_keytab_t"):
        return txt + "treat the files as kerberos keytab files."
    if f.endswith("_lock_t"):
        return txt + "treat the files as %s lock data, stored under the /var/lock directory" % prettyprint(f, "_lock_t")
    if f.endswith("_log_t"):
        return txt + "treat the data as %s log data, usually stored under the /var/log directory." % prettyprint(f, "_log_t")
    if f.endswith("_config_t"):
        return txt + "treat the files as %s configuration data, usually stored under the /etc directory." % prettyprint(f, "_config_t")
    if f.endswith("_conf_t"):
        return txt + "treat the files as %s configuration data, usually stored under the /etc directory." % prettyprint(f, "_conf_t")
    if f.endswith("_exec_t"):
        return txt + "transition an executable to the %s_t domain." % f[:-len("_exec_t")]
    if f.endswith("_cgi_content_t"):
        return txt + "treat the files as %s cgi content." % prettyprint(f, "_cgi_content_t")
    if f.endswith("_rw_content_t"):
        return txt + "treat the files as %s read/write content." % prettyprint(f, "_rw_content_t")
    if f.endswith("_rw_t"):
        return txt + "treat the files as %s read/write content." % prettyprint(f, "_rw_t")
    if f.endswith("_write_t"):
        return txt + "treat the files as %s read/write content." % prettyprint(f, "_write_t")
    if f.endswith("_db_t"):
        return txt + "treat the files as %s database content." % prettyprint(f, "_db_t")
    if f.endswith("_ra_content_t"):
        return txt + "treat the files as %s read/append content." % prettyprint(f, "_ra_conten_t")
    if f.endswith("_cert_t"):
        return txt + "treat the files as %s certificate data." % prettyprint(f, "_cert_t")
    if f.endswith("_key_t"):
        return txt + "treat the files as %s key data." % prettyprint(f, "_key_t")

    if f.endswith("_secret_t"):
        return txt + "treat the files as %s secret data." % prettyprint(f, "_key_t")

    if f.endswith("_ra_t"):
        return txt + "treat the files as %s read/append content." % prettyprint(f, "_ra_t")

    if f.endswith("_ro_t"):
        return txt + "treat the files as %s read/only content." % prettyprint(f, "_ro_t")

    if f.endswith("_modules_t"):
        return txt + "treat the files as %s modules." % prettyprint(f, "_modules_t")

    if f.endswith("_content_t"):
        return txt + "treat the files as %s content." % prettyprint(f, "_content_t")

    if f.endswith("_state_t"):
        return txt + "treat the files as %s state data." % prettyprint(f, "_state_t")

    if f.endswith("_files_t"):
        return txt + "treat the files as %s content." % prettyprint(f, "_files_t")

    if f.endswith("_file_t"):
        return txt + "treat the files as %s content." % prettyprint(f, "_file_t")

    if f.endswith("_data_t"):
        return txt + "treat the files as %s content." % prettyprint(f, "_data_t")

    if f.endswith("_file_t"):
        return txt + "treat the data as %s content." % prettyprint(f, "_file_t")

    if f.endswith("_tmp_t"):
        return txt + "store %s temporary files in the /tmp directories." % prettyprint(f, "_tmp_t")
    if f.endswith("_etc_t"):
        return txt + "store %s files in the /etc directories." % prettyprint(f, "_tmp_t")
    if f.endswith("_home_t"):
        return txt + "store %s files in the users home directory." % prettyprint(f, "_home_t")
    if f.endswith("_tmpfs_t"):
        return txt + "store %s files on a tmpfs file system." % prettyprint(f, "_tmpfs_t")
    if f.endswith("_unit_file_t"):
        return txt + "treat files as a systemd unit file."
    if f.endswith("_htaccess_t"):
        return txt + "treat the file as a %s access file." % prettyprint(f, "_htaccess_t")

    return txt + "treat the files as %s data." % prettyprint(f, "_t")

all_attributes = None


def get_all_attributes():
    global all_attributes
    if not all_attributes:
        all_attributes = map(lambda x: x['name'], info(ATTRIBUTE))
    return all_attributes


def policy(policy_file):
    global all_domains
    global all_attributes
    global bools
    global all_types
    global role_allows
    global users
    global roles
    global file_types
    global port_types
    global selinuxpolicy
    all_domains = None
    all_attributes = None
    bools = None
    all_types = None
    role_allows = None
    users = None
    roles = None
    file_types = None
    port_types = None
    try:
        selinuxpolicy = setools.SELinuxPolicy(policy_file)

    except:
        raise ValueError(_("Failed to read %s policy file") % policy_file)

try:
    policy_file = get_installed_policy()
    policy(policy_file)
except ValueError, e:
    if selinux.is_selinux_enabled() == 1:
        raise e


def _dict_has_perms(dict, perms):
    for perm in perms:
        if perm not in dict[PERMS]:
            return False
    return True


def gen_short_name(setype):
    all_domains = get_all_domains()
    if setype.endswith("_t"):
        domainname = setype[:-2]
    else:
        domainname = setype
    if domainname + "_t" not in all_domains:
        raise ValueError("domain %s_t does not exist" % domainname)
    if domainname[-1] == 'd':
        short_name = domainname[:-1] + "_"
    else:
        short_name = domainname + "_"
    return (domainname, short_name)


def get_bools(setype):
    bools = []
    domainbools = []
    domainname, short_name = gen_short_name(setype)
    for i in map(lambda x: x['boolean'], filter(lambda x: 'boolean' in x, search([ALLOW], {'source': setype}))):
        for b in i:
            if not isinstance(b, tuple):
                continue
            try:
                enabled = selinux.security_get_boolean_active(b[0])
            except OSError:
                enabled = b[1]
            if b[0].startswith(short_name) or b[0].startswith(domainname):
                if (b[0], enabled) not in domainbools and (b[0], not enabled) not in domainbools:
                    domainbools.append((b[0], enabled))
            else:
                if (b[0], enabled) not in bools and (b[0], not enabled) not in bools:
                    bools.append((b[0], enabled))
    return (domainbools, bools)

booleans = None


def get_all_booleans():
    global booleans
    if not booleans:
        booleans = selinux.security_get_boolean_names()[1]
    return booleans

booleans_dict = None
import gzip


def policy_xml(path="/usr/share/selinux/devel/policy.xml"):
    try:
        fd = gzip.open(path)
        buf = fd.read()
        fd.close()
    except IOError:
        fd = open(path)
        buf = fd.read()
        fd.close()
    return buf


def gen_bool_dict(path="/usr/share/selinux/devel/policy.xml"):
    global booleans_dict
    if booleans_dict:
        return booleans_dict
    import xml.etree.ElementTree
    import re
    booleans_dict = {}
    try:
        tree = xml.etree.ElementTree.fromstring(policy_xml(path))
        for l in tree.findall("layer"):
            for m in l.findall("module"):
                for b in m.findall("tunable"):
                    desc = b.find("desc").find("p").text.strip("\n")
                    desc = re.sub("\n", " ", desc)
                    booleans_dict[b.get('name')] = (m.get("name"), b.get('dftval'), desc)
                for b in m.findall("bool"):
                    desc = b.find("desc").find("p").text.strip("\n")
                    desc = re.sub("\n", " ", desc)
                    booleans_dict[b.get('name')] = (m.get("name"), b.get('dftval'), desc)
            for i in tree.findall("bool"):
                desc = i.find("desc").find("p").text.strip("\n")
                desc = re.sub("\n", " ", desc)
                booleans_dict[i.get('name')] = ("global", i.get('dftval'), desc)
        for i in tree.findall("tunable"):
            desc = i.find("desc").find("p").text.strip("\n")
            desc = re.sub("\n", " ", desc)
            booleans_dict[i.get('name')] = ("global", i.get('dftval'), desc)
    except IOError, e:
        pass
    return booleans_dict


def boolean_category(boolean):
    booleans_dict = gen_bool_dict()
    if boolean in booleans_dict:
        return _(booleans_dict[boolean][0])
    else:
        return _("unknown")


def boolean_desc(boolean):
    booleans_dict = gen_bool_dict()
    if boolean in booleans_dict:
        return _(booleans_dict[boolean][2])
    else:
        desc = boolean.split("_")
        return "Allow %s to %s" % (desc[0], " ".join(desc[1:]))


def get_os_version():
    os_version = ""
    pkg_name = "selinux-policy"
    try:
        import commands
        rc, output = commands.getstatusoutput("rpm -q '%s'" % pkg_name)
        if rc == 0:
            os_version = output.split(".")[-2]
    except:
        os_version = ""

    if os_version[0:2] == "fc":
        os_version = "Fedora" + os_version[2:]
    elif os_version[0:2] == "el":
        os_version = "RHEL" + os_version[2:]
    else:
        os_version = ""

    return os_version


def reinit():
    global all_attributes
    global all_domains
    global all_types
    global booleans
    global booleans_dict
    global bools
    global fcdict
    global file_types
    global local_files
    global methods
    global methods
    global portrecs
    global portrecsbynum
    global port_types
    global role_allows
    global roles
    global login_mappings
    global selinux_user_list
    global user_types
    all_attributes = None
    all_domains = None
    all_types = None
    booleans = None
    booleans_dict = None
    bools = None
    fcdict = None
    file_types = None
    local_files = None
    methods = None
    methods = None
    portrecs = None
    portrecsbynum = None
    port_types = None
    role_allows = None
    roles = None
    user_types = None
    login_mappings = None
    selinux_user_list = None
