# OTA:file:ota.py
# OTA:reboot:true
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


def get_headers(message):
    last_index = 0
    index = 0
    done = False
    headers = {}
    while not done:
        current_newline = message.index('\n', index)
        current_line = message[index: current_newline]
        last_index = index
        index = current_newline + 1
        if not current_line.startswith('# OTA:'):
            done = True
        else:
            line_split = current_line.split(":")
            if len(line_split) == 3:
                print(f"Found OTA header: {line_split[1]} = {line_split[2]}")
                headers[line_split[1].strip()] = line_split[2].strip()
            else:
                print("Bad format for header.  Format is something like '# OTA:file:main.py'")
    return headers, last_index


def process_ota_msg(msg):
    print("Got OTA message...")
    ota_fields, body_start = get_headers(msg)

    if ota_fields:
        print(f"Found file header and data to write, writing to {ota_fields['file']}")
        with open(ota_fields['file'], 'w') as file:
            if ota_fields['file'].endswith('.py'):
                file.write(msg)
            else:
                file.write(msg[body_start:])
        print("Wrote new version")
        if 'reboot' in ota_fields and ota_fields['reboot'] == 'true':
            print("Rebooting...")
            machine.reset()
    else:
        print("No ota headers.")
