# SELinux Userspace release process

1. Make sure everything builds and works to the best of your ability
    
1. Check abi-compliance-checker

1. Bump the */VERSION files (e.g. to 3.1-rc1) and commit them

        find . -name VERSION | xargs sed -i 's/.*/3.0-rc1/'
	
1. Run `scripts/release`` to generate the tags and tarballs

## 5. Push changes

    git push && git push --tags

## 6. Create release changelog and shortlog

    git shortlog <prior-release-tag>..<new-release-tag> > shortlog-<new-release-tag>.txt
	
	git log <prior-release-tag>..<new-release-tag> > log-<new-release-tag>.txt

## 7. Create release notes document

Call it `RELEASE-<newrelease>.txt** and fill it with release notes summarizing
user-visible changes, important fixes, etc. 

## 8. Update Releases.md page

Use the output from the release script. After   commit the updated page and
tarballs and push selinux.wiki 

## 9. Create a new GitHub release

Upload the manually-created tarballs along with the shortlog, log and RELEASE
files - these show up as Assets under the release, see the last one at
https://github.com/SELinuxProject/selinux/releases.  
