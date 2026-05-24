@echo off
cd /d "C:\Users\EXPPlus3Paymon\Documents\Codex\Full-Screen-Clock"
git add -A
git commit -m "perf: fix CPU/memory spike - cache PIL image, lower resize cost"
git push origin main
echo Done
