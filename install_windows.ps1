Invoke-WebRequest https://www.python.org/ftp/python/3.10.6/python-3.10.6-embed-amd64.zip -OutFile .\tmp\python.zip
Expand-Archive -Path .\tmp\python.zip -DestinationPath .\python_temp
Remove-Item .\tmp\python.zip
