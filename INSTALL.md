# INSTALL.md for the Swarm-Alphabet Project

## Simple Procedure

You can run the command from the root directory of the project repository.
`./scripts/install.sh`.

## Custom Procedure
**You can skip the first three steps if you have virtualenv installed.**
1. Firstly we must check whether `Python 3` is installed.&nbsp;
> ` python3 --version`

- You should get an output `Python 3.5.2` or higher

2.Next we must install `pip` on the machine.
> `apt-get install python3-pip`

3.Now we must install `virtualenv` to separate our project's environmen from the global python environemnt.
> `pip3 install virtualenv`.

4.Navigate to the root of the project's directory to create the virtual environment using:
> `virtualenv <virtualenv name>`

5.We must activate the virtual environment to use it.
> `source <virtualenv name>/bin/activate`

6.To install the dependencies, run:
> `pip install -r requirements.txt`

7.To verify whether the installation is successful:
> `python ./scripts/package_test.py`

8.You can choose to delete the install verification file using:
> `rm -rf ./scripts/package_test.py`

*Do not forget to prefix **sudo** to the required commands if you are not root user.*