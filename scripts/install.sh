currentDir=$(pwd) &> /dev/null
sudo apt-get install python3-pip &> /dev/null
python_version=$(python3 --version)
pip3 install virtualenv &> /dev/null
venv_name='swarmAlphabet'
virtualenv $venv_name
source $venv_name/bin/activate
pip install -r requirements.txt
test=$(python ./scripts/package_test.py)
if [ $? -eq 0 ]
then
	echo "Installation Succesful."
else
	echo $test
fi
rm -rf ./scripts/package_test.py
echo ""
echo "Use the command 'source $venv_name/bin/activate' to activate the virtual env after changing to the current directory."