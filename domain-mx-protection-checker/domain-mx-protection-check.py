import dns.resolver
import re
import os
import sys

email_list = 'emails.txt'

# Check if the file exists
if not os.path.exists(email_list):
    print(f"\n--- PLEASE FIX THE FOLLOWING ERROR: --------------------------------------------------------")
    print(f"= The file 'emails.txt' does not exist.")
    print(f"= Create an email.txt file, save the email addresses, one line per email address.")
    print(f"--------------------------------------------------------------------------------------------\n")
    sys.exit(1)

# Check file is empty
if os.path.getsize(email_list) == 0:
    print(f"\n--- PLEASE FIX THE FOLLOWING ERROR: ---------------------------------------------------------")
    print(f"= The file is empty.")
    print(f"= Create an email.txt file, save the email addresses, one line per email address.")
    print(f"--------------------------------------------------------------------------------------------\n")
    sys.exit(1)

# Read email addresses from a file
with open('emails.txt', 'r') as file:
    emails = [line.strip() for line in file]

# Regular expression pattern for valid domain format
domain_pattern = r'^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\.)+[A-Za-z]{2,12}$'

# Function to extract domain from email address
def get_domain(email):
    domain = email.split('@')[-1]
    if re.match(domain_pattern, domain):
        return domain
    else:
        return None

# Function to get MX record with the lowest priority for a domain
def get_lowest_priority_mx(domain):
    try:
        resolver = dns.resolver.Resolver()
        mx_records = resolver.resolve(domain, 'MX')
        lowest_priority = min(mx_records, key=lambda rec: rec.preference)
        return lowest_priority.exchange.to_text(), lowest_priority.preference
    except dns.resolver.NXDOMAIN:
        return f"Domain {domain} does not exist", None
    except dns.exception.DNSException as e:
        return f"Error fetching MX records: {e}", None

# Extract unique domains from email list
domains = set(filter(None, map(get_domain, emails)))

# Open output file for writing valid domains
with open('output.txt', 'w') as output_file:
    # Fetch MX record with the lowest priority for each domain
    print(f"\n=============================================================================================")
    print(f"= PROCESSED")
    print(f"=============================================================================================")
    for domain in domains:
        mx_record, priority = get_lowest_priority_mx(domain)
        if priority is not None:
            output_line = f"{domain}\t{mx_record}\t{priority}"
            output_file.write(output_line + '\n')
            print(">>", output_line)  # Print output to the screen

# Save invalid email addresses to a separate file
invalid_emails = [email for email in emails if get_domain(email) is None]
if invalid_emails:
    with open('invalid-domains.txt', 'w') as invalid_file:
        for email in invalid_emails:
            invalid_file.write(email + '\n')
    print(f"\n---------------------------------------------------------------------")
    print(f"INVALID DOMAIN/S: [ {len(invalid_emails)} ] (see invalid-domains.txt)")
    print(f"---------------------------------------------------------------------") 