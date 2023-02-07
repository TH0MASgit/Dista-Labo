#!/bin/bash
# Make sure you have dista's ssh key before running this script


# == Step 1: Initial configuration ==
coderoot="$HOME/code"
dataroot="$HOME/data"
utilroot="$HOME/util"

# Let's create these directories before going further:
mkdir -p "$coderoot" "$dataroot" "$utilroot"


# == Step 2: Clone the git repository to ~/code/dista ==
echo "Cloning git repo ========================================================"
distapath="'$coderoot/dista'"

if [ -d $distapath ] ; then
    cd $distapath
    git init
    git remote add origin git@github.com:doorjuice/dista.git
    git fetch
    git checkout -t origin/master
else
    git clone git@github.com:doorjuice/dista.git $distapath
    cd $distapath
fi

# For backwards compatibility with earlier installs:
ln -s $distapath ~/Documents/dista

# We should "reconnect" the subtrees as well:
git remote add logisticam git@github.com:distaCAL/logisticam.git

# Speaking of, here's the second repo (shared with InnovLog):
if [ ! -d "$coderoot/logisticam" ] ; then
    git clone git@github.com:distaCAL/logisticam.git "$coderoot/logisticam"
fi


# == Step 3: Configure the user's git credentials ==
# Everyone should set up their own user.name and user.email, but by default we
# have a "shared" github account: Dista <dista@claurendeau.qc.ca>
echo "Configuring git ========================================================="
cd $distapath
if [ -z "$(git config --global --get user.name)" ] ; then
    git config --global user.name "Dista"
    git config --global user.email "dista@claurendeau.qc.ca"
elif [ -z "$(git config --local --get user.name)" ] ; then
   git config user.name "Dista"
   git config user.email "dista@claurendeau.qc.ca"
fi

git status
exit $?

