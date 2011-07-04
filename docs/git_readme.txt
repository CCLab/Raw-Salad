This file contains some pieces of advice that would help us to avoid problems with Git.

1. Repositories diagram.

The following diagram will show what happens when we do git push all:

local machine               github             server/repo/rawsalad.git                    server/projects/rawsalad       server

      |  changes in files      |                           |                                             |                   |
      |----------------------->|                           |                                             |                   |
      |                        |                           |                                             |                   |
      |              changes in files                      |                                             |                   |
      |--------------------------------------------------->|                                             |                   |
      |                        |                           |                                             |                   |
      |                        |                           |    when rawsalad.git updates, it makes      |                   |
      |                        |                           |    projects/rawsalad to pull from it        |                   |
      |                        |                           |-------------------------------------------->|                   |
      |                        |                           |                                             |                   |
      |                        |                           |                 restart-app                 |                   |
      |                        |                           |---------------------------------------------------------------->|
      |                        |                           |                                             |                   |
      |                        |                           |   now we can see changes on the site        |                   |
      |                        |                           |                                             |                   |
      
When anything fails, actions which follow it won't be started.

2. What was the reason of problems with git on server?

Repo projects/rawsalad is almost(about differences in 3.) the same repo which we have on our local machines.
It only pulls from repo/rawsalad.git.

When we change any file in projects/rawsalad manually and then push changes in this file, this will happen:
1) local machine, github, repo/rawsalad.git have version A of a file
2) projects/rawsalad has version B of a file
3) projects/rawsalad tries to pull from rawsalad.git and then BAAAM, it fails because git wants projects/rawsalad to commit
   changes before pulling so that it can merge(!!!).
   
The same thing happens when new files are added.

IMPORTANT: Any unconscious changes made manually to projects/rawsalad are likely to cause problems.

However, there is a way to change some files in repo without causing problems for git. The following section covers this subject.

3. Changing files in projects/rawsalad without affecting git.

I found a simple and brutal way to do it: move a file out of directory with repo, update repo and copy the file back(of course
there is a script that does this thing automatically on every update).
There is 1 drawback to this method: when we want to change such file, we can't do it by pushing to git, but it must be done
manually.

The second way is desctribed in 6.

In our case, there is one file that is different in projects/rawsalad than in github: it's src/rawsalad/settings.py.

4. How to recognize when git on server didn't update?

After writing password to server to update repos on it, git will print some information in console. When update fails,
there should be an information about it, so look at what git says:). It will make it easier to catch a failure.

5. I was playing in projects/rawsalad and I'm not sure if everyhing is ok. How to check it?

To do this, go to projects/rawsalad directory and write in a console: git status.
The files that will be listed there are the differences, so the only files that appear, should be files that are
consciously made different on server than on github.
So, now only src/rawsalad/settings.py should be on this list.

6. Adding a new file to the repo on server without adding to it to github.

[change]

To do this, we have to tell git that this file should be ignored locally(only on this repo), but
(!!) this will work if the file will not be added to github in the future.
To add such a file( e.g. abc.xyz ) open: projects/rawsalad/.git/info/exclude
and append a new line with the name of the file to exclude.
For example, now there are four such files: dd_budg2011_go.json, dd_budg2011_tr.json, dd_fund2011_tr.json and  fundtr.json.
