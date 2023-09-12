import argparse
import re
import time
import json
from selenium import webdriver

# Create a command-line argument parser
parser = argparse.ArgumentParser(description="Marketplace Scraper")

# Define command-line arguments
parser.add_argument("--json_file", required=True, help="Path to a JSON file containing user and URLs information")
parser.add_argument("--cookies", help="Cookies to send (if any), formatted as 'name1=value1; name2=value2'")

# Parse the command-line arguments
args = parser.parse_args()

# Read the JSON object from the input file
with open(args.json_file, 'r') as json_file:
    json_data = json.load(json_file)

# Extract user and URLs information from the JSON object
user_email = json_data.get("user", "")
urls = json_data.get("urls", {})

# Set up a headless Firefox WebDriver
options = webdriver.FirefoxOptions()
options.headless = True

# Create the Firefox WebDriver with the specified options
driver = webdriver.Firefox(options=options)

# Get the current Unix timestamp
current_timestamp = str(int(time.time()))

# Initialize an empty result content
result_content = ''

# Loop through each URL in the dictionary and append the content to the result
for url_name, url in urls.items():
    # Navigate to the URL and let JavaScript run
    driver.get(url)

    # Wait for JavaScript to finish executing (you can add more specific waits as needed)
    driver.implicitly_wait(10)

    # Get the page source
    page_source = driver.page_source

    # Define the marker to search for in the page source
    marker = '{"require":[["ScheduledServerJS","handle",null,[{"__bbox":{"require":[["RelayPrefetchedStreamCache","next",[],["adp_CometMarketplaceSearchContentContainerQueryRelayPreloader_'

    # Use regular expressions to extract content including the marker
    match = re.search(re.escape(marker) + '(.*)', page_source, re.DOTALL)

    if match:
        content_with_marker = match.group(0)
    else:
        content_with_marker = page_source

    # Find the index of the first occurrence of </script> and remove content after it
    script_end_index = content_with_marker.find('</script>')
    if script_end_index != -1:
        content_with_marker = content_with_marker[:script_end_index]

    # Append the content to the result with a newline character
    result_content += f"URL Name: {url_name}\n"
    result_content += content_with_marker + '\n'

# Generate the output file name based on the current Unix timestamp
output_file = f"{current_timestamp}_{user_email}.txt"

# Save the resulting HTML to the output file
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(result_content)

# Quit the WebDriver
driver.quit()

# Print the name of the output file
print("Output saved to:", output_file)
