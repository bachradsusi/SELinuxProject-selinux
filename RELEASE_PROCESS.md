# SELinux Userspace release process

1. Make sure everything builds and works to the best of your ability

    Follow [README.md](README.md) and try to build and install sources to a private directory, or/and as the default system libraries and binaries. 

    Run `make test` on system with installed sources, or/and using `./scripts/env_use_destdir`

2. Check [abi-compliance-checker](http://lvc.github.io/abi-compliance-checker/) results

        TEMPDIR=$(mktemp -d)
        cd $TEMPDIR
        git clone https://github.com/SELinuxProject/selinux.git selinux-master
        cd selinux-master
        VERSION=$(cat libsepol/VERSION)
        git worktree add ../selinux-$VERSION libsepol-$VERSION
        cd ..
        
        export CFLAGS="-g -Og -pipe -Wall -Werror=format-security -Wp,-D_FORTIFY_SOURCE=2 -Wp,-D_GLIBCXX_ASSERTIONS -fexceptions -fstack-protector-strong -grecord-gcc-switches -specs=/usr/lib/rpm/redhat/redhat-hardened-cc1 -specs=/usr/lib/rpm/redhat/redhat-annobin-cc1 -m64 -mtune=generic -fasynchronous-unwind-tables -fstack-clash-protection -fcf-protection -fcommon"
        
        for i in $VERSION master; do
          cd selinux-$i
          make DESTDIR=$TEMPDIR/build-$i install install-rubywrap install-pywrap
          cd ..
        done
        
        for i in libsepol libselinux libsemanage; do
          abi-dumper -o $i-$VERSION.dump build-$VERSION/usr/lib/$i.so -lver $VERSION -public-headers selinux-$VERSION/$i/include
          abi-dumper -o $i-master.dump build-master/usr/lib/$i.so -lver master -public-headers selinux-master/$i/include
          abi-compliance-checker -l $i -old $i-$VERSION.dump -new $i-master.dump
        done

    Results are stored in `compat_reports/{libsepol,libselinux,libsemanage}/$VERSION_to_master/compat_report.html` files

3. Bump the */VERSION files (e.g. to 3.1-rc1) and commit them

        find . -name VERSION | xargs sed -i 's/.*/3.0-rc1/'
	
4. Run `scripts/release`` to generate the tags and tarballs

5. Push changes

        git push && git push --tags

6. Create release changelog and shortlog

        git shortlog <prior-release-tag>..<new-release-tag> > shortlog-<new-release-tag>.txt
	
	    git log <prior-release-tag>..<new-release-tag> > log-<new-release-tag>.txt

7. Create release notes document

    Call it `RELEASE-<newrelease>.txt** and fill it with release notes summarizing
    user-visible changes, important fixes, etc. 

8. Update Releases.md page

    Use the output from the release script. After   commit the updated page and
    tarballs and push selinux.wiki 

9. Create a new GitHub release

    Upload the manually-created tarballs along with the shortlog, log and RELEASE
    files - these show up as Assets under the release, see the last one at
    https://github.com/SELinuxProject/selinux/releases.  
