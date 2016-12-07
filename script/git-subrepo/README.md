# git subrepo

Merge sub git repo into sub-directory in a parent git dir with git-submerge.
git-subrepo reads config from ".gitsubrepo" resides in the root of parent
git working dir.

## Usage

Configure file ".gitsubrepo" syntax:

```
    # set base of remote url to "https://github.com/"
    [ remote: https://github.com/ ]

    # set base of local dir to "plugin"
    [ base: plugin ]

    # <local dir>   <remote uri>            <ref to fetch>
    gutter          airblade/vim-gitgutter  master

    # if <remote uri> ends with "/", <local dir> will be added after "/"
    ansible-vim     DavidWittman/           master

    # change base to "root"
    [ base: ]

    # use a specific commit 1a2b3c4
    ultisnips       SirVer/                 1a2b3c4
```

With above config, "git subrepo" will:

-   fetch master of https://github.com/DavidWittman/ansible-vim
    and put it in:
        <git-root>/plugin/ansible-vim

-   fetch master of https://github.com/airblade/vim-gitgutter
    and put it in:
        <git-root>/plugin/gutter

-   fetch commit 1a2b3c4 of https://github.com/SirVer/ultisnips
    and put it in:
        <git-root>/ultisnips
