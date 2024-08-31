$pythonScript = ".\cohere_probe.py"
$command = 'python -W "ignore:" ' + $pythonScript
Invoke-Expression $command
