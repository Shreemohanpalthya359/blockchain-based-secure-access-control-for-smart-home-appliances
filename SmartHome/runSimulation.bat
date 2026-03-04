@echo off
echo Starting Truffle Develop...
start "Truffle Develop" cmd /k "cd /d C:\Users\CH.RAJA SRICHARAN\Downloads\Blockchain\Blockchain\hello-eth && npx truffle develop"
echo Waiting for Truffle to start...
timeout /t 5 /nobreak > nul
echo Running IOT Simulation...
cd /d C:\Users\CH.RAJA SRICHARAN\Downloads\Blockchain\Blockchain\SmartHome
python IOTSimulation.py
pause

