@echo off
cd /d "C:\Users\EXPPlus3Paymon\Documents\Codex\Full-Screen-Clock"
del _git_push.bat
git add -A
git commit -m "Remove temp build script"
git push origin main
echo Done
