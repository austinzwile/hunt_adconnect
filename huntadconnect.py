import ldap3
import re
import validators
import getpass
from argparse import ArgumentParser

def find_adconnect_server(domain, username, password):
        target_dn = ""
        DC = domain.split(".")
        DC_len = len(DC)
        iter = 1

        for DC in domain.split("."):
                target_dn += "DC={}".format(DC)
                if iter < DC_len:
                        target_dn += ","
                iter += 1

        user = "{}\\{}".format(domain, username)
        server = ldap3.Server(domain)

        connection = ldap3.Connection(server = server, user = user, password = password, authentication = ldap3.NTLM)
        connection.bind()
        print()
        connection.search(target_dn,"(description=*configured to synchronize to tenant*)", attributes=["description"])

        adconnect_servers = connection.entries

        for entry in adconnect_servers:
                print(str(entry) + "\n")

def main():
        parser = ArgumentParser(description="Hunt down the Azure AD Connect server.", usage="\npython findadconnect.py target\n")
        parser.add_argument("target", type=str, help="domain/username[:password]")
        args = parser.parse_args()

        username = ""
        password = ""
        domain = ""

        connection_string = args.target
        try:
                s = connection_string.split("/")
                if len(s) != 2:
                        raise Exception("Error: incorrectly formatted target string.")

                domain = s[0]
                username_and_pass = s[1]
                domain_check = validators.domain(domain)

                if domain_check:
                        pass
                else:
                        raise Exception("Error: invalid domain provided in target string.")

                if ":" in username_and_pass:
                        s = username_and_pass.split(":")
                        username = s[0]
                        password = s[1]
                else:
                        username = username_and_pass

                validuser = not(any(ele in username for ele in [*"\"/\[]:;|=,+*?<>"]))

                if not validuser:
                        raise Exception("Error: invalid characters found in the Active Directory username.")

        except Exception as e:
                print(str(e))
                parser.print_help()
                exit()

        if not password:
                password = getpass.getpass("Password: ")

        find_adconnect_server(domain, username, password)
if __name__ == "__main__":
        main()
