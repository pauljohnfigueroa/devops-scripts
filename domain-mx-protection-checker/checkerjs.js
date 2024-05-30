const fs = require('fs');
const dns = require('dns');

// Read email addresses from a file
const emails = fs.readFileSync('emails.txt', 'utf-8').trim().split('\n');

// Regular expression pattern for valid domain format
const domainPattern = /^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\.)+[A-Za-z]{2,6}$/;

// Function to extract domain from email address
function getDomain(email) {
  const domain = email.split('@')[1];
  return domainPattern.test(domain) ? domain : null;
}

// Function to get MX record with the lowest priority for a domain
function getLowestPriorityMX(domain) {
  return new Promise((resolve, reject) => {
    dns.resolveMx(domain, (err, addresses) => {
      if (err) {
        if (err.code === 'ENODATA') {
          resolve([`Domain ${domain} does not exist`, null]);
        } else {
          resolve([`Error fetching MX records: ${err.message}`, null]);
        }
      } else {
        const lowestPriority = addresses.sort(
          (a, b) => a.priority - b.priority
        )[0];
        resolve([lowestPriority.exchange, lowestPriority.priority]);
      }
    });
  });
}

// Extract unique domains from email list
const domains = new Set(emails.map(getDomain).filter(Boolean));

// Fetch MX record with the lowest priority for each domain
async function processEmails() {
  const validOutput = [];
  const invalidEmails = [];

  for (const domain of domains) {
    const [mx, priority] = await getLowestPriorityMX(domain);
    if (priority !== null) {
      const outputLine = `${domain}\t${mx}\t${priority}`;
      validOutput.push(outputLine);
      console.log(outputLine);
    }
  }

  fs.writeFileSync('output.txt', validOutput.join('\n') + '\n');

  for (const email of emails) {
    const domain = getDomain(email);
    if (domain === null) {
      invalidEmails.push(email);
    }
  }

  if (invalidEmails.length > 0) {
    fs.writeFileSync('invalid-domains.txt', invalidEmails.join('\n') + '\n');
    console.log(
      `===================================================================================================
The following ${invalidEmails.length} email addresses are invalid and were saved in 'invalid-domains.txt':
===================================================================================================`
    );
    console.log(invalidEmails.join('\n'));
  }
}

processEmails();
