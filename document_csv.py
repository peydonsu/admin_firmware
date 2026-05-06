import pandas as pd
import re

def extract_names_and_emails(file_path):
    """
    Extract just names and emails from broken CSV.
    """
    data = []
    
    with open(file_path, 'r') as file:
        # Skip header
        next(file)
        
        for line in file:
            if not line.strip():
                continue
                
            parts = line.strip().split(',')
            
            # Extract name components (first 3 fields)
            first_name = parts[0].strip() if len(parts) > 0 else ''
            middle_name = parts[1].strip() if len(parts) > 1 else ''
            last_name = parts[2].strip() if len(parts) > 2 else ''
            
            # Find email anywhere in the line
            email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', line)
            email = email_match.group(0) if email_match else ''
            
            # Find email label (Home, School, etc.)
            email_label = ''
            if email:
                # Look for common labels before the email
                for i, part in enumerate(parts):
                    if email in part and i > 0:
                        candidate = parts[i-1]
                        if candidate in ['Home', 'School', 'Work', '* myContacts,*']:
                            email_label = candidate
                            break
            
            # Extract birthday if present
            birthday_match = re.search(r'\d{4}-\d{2}-\d{2}', line)
            birthday = birthday_match.group(0) if birthday_match else ''
            
            data.append({
                'Full Name': f"{first_name} {middle_name} {last_name}".strip().replace('  ', ' '),
                'First Name': first_name,
                'Last Name': last_name,
                'Email': email,
                'Email Type': email_label,
                'Birthday': birthday
            })
    
    return pd.DataFrame(data)

def extract_contacts_with_labels(file_path):
    """
    Extract contacts with proper email label detection.
    """
    data = []
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        # Print header for reference
        header = lines[0].strip().split(',')
        print(f"Header has {len(header)} columns\n")
        
        for line_num, line in enumerate(lines[1:], start=2):
            if not line.strip():
                continue
            
            parts = line.strip().split(',')
            
            # Basic info
            first_name = parts[0].strip() if len(parts) > 0 else ''
            last_name = parts[2].strip() if len(parts) > 2 else ''
            
            # Find ALL emails and their potential labels
            emails_found = []
            
            # Scan through all parts to find emails and what comes before them
            for i, part in enumerate(parts):
                if '@' in part and '.' in part:  # Likely an email
                    email = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', part)
                    if email:
                        email_value = email.group(0)
                        
                        # Look for label (could be in previous part or same part)
                        label = 'Other'
                        
                        # Check the part right before this one
                        if i > 0:
                            prev_part = parts[i-1].strip()
                            if prev_part in ['Home', 'School', 'Work', '* myContacts,*', 'Other']:
                                label = prev_part
                            elif 'myContacts' in prev_part:
                                label = 'Google Contacts'
                        
                        # Also check if label is in the same part (before the @ symbol)
                        if '@' in part and ',' not in part:
                            # Sometimes label is attached: "Home,franksu@gmail.com" 
                            # becomes one part with comma already split
                            pass
                        
                        emails_found.append({
                            'email': email_value,
                            'label': label,
                            'position': i
                        })
            
            # Also search the raw line for patterns like "Label,email"
            raw_line = line.strip()
            label_email_pattern = r'(Home|School|Work|\* myContacts,\*),([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            matches = re.findall(label_email_pattern, raw_line)
            
            for label, email in matches:
                # Check if we already found this email
                if not any(e['email'] == email for e in emails_found):
                    emails_found.append({
                        'email': email,
                        'label': label,
                        'position': -1
                    })
            
            # Create contact record
            contact = {
                'First Name': first_name,
                'Last Name': last_name,
                'Full Name': f"{first_name} {last_name}".strip(),
                'Birthday': re.search(r'\d{4}-\d{2}-\d{2}', line).group(0) if re.search(r'\d{4}-\d{2}-\d{2}', line) else ''
            }
            
            # Add emails with their labels
            for i, email_info in enumerate(emails_found):
                contact[f'Email {i+1} - Label'] = email_info['label']
                contact[f'Email {i+1} - Value'] = email_info['email']
            
            data.append(contact)
    
    return pd.DataFrame(data)

# Run the parser
df = extract_contacts_with_labels("contacts.csv")

print("=== Contacts with Email Labels ===\n")
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
print(df.to_string(index=False))

# Run extraction
df_clean = extract_names_and_emails("contacts.csv")
print(df_clean)
# Quick test to show label detection works
test_row = "Exploit,Windows,10,,,,,,,,Home,,,,,,* myContacts,* ,franksusu68@gmail.com"
parts = test_row.split(',')

print("Parts array:")
for i, part in enumerate(parts):
    print(f"  [{i}] = '{part}'")

print("\nScanning for emails and labels:")
for i, part in enumerate(parts):
    if '@' in part:
        print(f"  Found email at position {i}: '{part}'")
        if i > 0:
            print(f"    → Label candidate at position {i-1}: '{parts[i-1]}'")