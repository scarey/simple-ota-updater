import io
import machine

# Look for "header" lines to indicate the filename to update and whether to reboot afterward.
# "headers" come before the code and are of the format "# OTA:<header name>:<header value>"
# Currently supported "headers":
#  "file" - filename to write, e.g. main.py, subdir/xyz.py or any other text files
#  "reboot" - "true" or "false" whether the ESP32 should reboot after the "file" is written

# The OTA message could be read off an MQTT topic and maybe publish to a "version" topic as part of the startup code.
# With this quick and dirty approach, if the updated "file" has issues that will prevent listening to MQTT then OTA
# updates will stop working so you'll want to do some testing beforehand.

# See main.ota as an example of what would be published to the OTA topic for a simple LED blink main.py


def process_ota_msg(msg):
    print(f"Got OTA message: {msg}")
    ota_buf = io.StringIO(msg)
    headers_done = False
    ota_fields = {}
    current_line = None
    while not headers_done:
        current_line = ota_buf.readline()
        if current_line.startswith("# OTA:"):
            line_split = current_line.split(":")
            if len(line_split) == 3:
                print(f"Found OTA header: {line_split[1]} = {line_split[2]}")
                ota_fields[line_split[1].strip()] = line_split[2].strip()
            else:
                print("Bad format for header.  Format is something like '# OTA:file:main.py'")
        else:
            headers_done = True
            print(f"Found non header line")
    print(ota_fields)
    if 'file' in ota_fields and current_line:
        file_done = False
        print(f"Found file header and data to write, writing to {ota_fields['file']}")
        with open(ota_fields['file'], 'w') as file:
            file.write(current_line)
            while not file_done:
                current_line = ota_buf.readline()
                if current_line:
                    file.write(current_line)
                else:
                    file_done = True
        print("Wrote new version")
        if 'reboot' in ota_fields and ota_fields['reboot'] == 'true':
            print("Rebooting...")
            machine.reset()
    else:
        print("No file header or no data to write.")
