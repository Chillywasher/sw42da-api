class Sw42daUtility:

    def __init__(self):
        pass

    def get_status_dict(self, response: str):

        status_dict = {}
        values = ["Power", "IR", "IR_Mode", "Key", "Beep", "LCD", "LCD_PauseTime(S)", "PWLED_Follow", "Network", "Baud", "Temp(C)", "Uptime(Day:Hour:Min:Sec)"]
        values += ["ARC_Mode", "OpticalSel", "OpticalEn", "OutMode", "Audio"]
        values += ["CEC_Control", "CEC_ControlBy", "CEC_Steps"]
        values += ["MultiChannelOutFrom", "2ChannelOutFrom", "DRC", "SurroundDecoder(Upmixer)", "SpeakerVirtualizer"]

        for v in values:
            new_dict = self._get_single_key(v, response)
            status_dict = {**status_dict, **new_dict}

        t = self._status_table("AudioOut", response, "AudioOut")
        status_dict = {**status_dict, **t}

        t = self._status_table("Line Output", response, "LineOutput")
        status_dict = {**status_dict, **t}

        t = self._status_table("Dante Output", response, "DanteOutput")
        status_dict = {**status_dict, **t}

        return status_dict

    @staticmethod
    def _get_single_key(key_to_find: str, lines_to_check: list[str]):
        """

        Get a *single* key and value from the "key_to_find"

        returns: {"Power": "On"}

        example:

        Power   IR   IR_Mode   Key   Beep   LCD   LCD_PauseTime(S)   PWLED_Follow   Network   Baud     Temp(C)   Uptime(Day:Hour:Min:Sec)
        On      On   5v        On    Off    On    3                  On             Mode 2    57600    73.0C     0000:01:07:46

        Output     FromIn     HDMIcon     OutputEn     OSP     OutputScaler     AudioSignal
        01         01         On          Yes          SNK     Bypass           Bypass
        02         01         Off         Yes          SNK     Auto             Downmix 2CH

        ARC_Mode     OpticalSel      OpticalEn     OutMode     Audio
        Source       Downmix 2CH     On            5.1CH       None

        NB: Audio is contained as a single key and within AudioSignal

        """

        line_index = 0

        for line in lines_to_check:

            # remove any unneccsary whitespace and then add a space to end of line so we can match the exact key
            # e.g. match "Audio " in "AudioNot, NotAudio, Audio "
            line = line.strip() + " "
            key_to_find = key_to_find.strip() + " "

            # print(line)

            if line.find(key_to_find) > -1:
                split_keys = line.split("  ")# NB two spaces as some values contain a space
                keys = [s.strip() + " " for s in split_keys if s.strip()]
                # print(keys)

                value_pos = keys.index(key_to_find)
                # print("Value is on line", line_index+1, "at position", value_pos)

                split_values = lines_to_check[line_index + 1].split("  ")# NB two spaces as some values contain a space
                values = [v.strip() for v in split_values if v.strip()]

                # print(key_to_find, values[value_pos])
                value = values[value_pos]

                if value.isdigit():
                    value = int(value)

                return {key_to_find.strip(): value}

            line_index += 1

        return None

    @staticmethod
    def _status_table(key_to_find: str, lines_to_check: list[str], dict_list_key: str):

        """

        Gets an entire table

        returns: LineOutputs: [{}]

        example:

        Line Output             Volume     Mute     Delay(Ms)     GroupControlEn     CEC_ControlEn
        5.1CH Line L            59         Off      0             On                 On
        5.1CH Line R            59         Off      0             On                 On
        5.1CH Line Sub          59         Off      0             On                 On
        5.1CH Line C            59         Off      0             On                 On
        5.1CH Line Ls           59         Off      0             On                 On
        5.1CH Line Rs           59         Off      0             On                 On
        Downmix Line L          50         Off      0             On                 On
        Downmix Line R          50         Off      0             On                 On

        """

        return_list = []
        line_index = 0

        for line in lines_to_check:

            # remove any unneccsary whitespace and then add a space to end of line so we can match the exact key
            # e.g. match "Audio " in "AudioNot, NotAudio, Audio "
            line = line.strip() + " "
            key_to_find = key_to_find.strip() + " "

            # make sure value is at pos 0
            if line.find(key_to_find) == 0:
                split_keys = line.split("  ")# NB two spaces as some values contain a space

                # store the key labels
                keys = [s.strip() + " " for s in split_keys if s.strip()]
                # print("keys", keys)

                # value_pos = keys.index(key_to_find)
                # print("Table value is on line", line_index+1, "at position", value_pos)

                # iterate through the lines until come to a blank line, add dicts to the list

                # the values are on the next line, after the key labels
                split_values = lines_to_check[line_index + 1].split("  ")# NB two spaces as some values contain a space
                values = [v.strip() for v in split_values if v.strip()]

                while values:

                    # print("values", values)

                    line_dict = {}

                    for i in range(len(keys)):

                        value = values[i].strip()

                        if value.isdigit():
                            value = int(value)

                        line_dict[keys[i].strip()] = value

                    return_list.append(line_dict)

                    line_index += 1
                    split_values = lines_to_check[line_index + 1].split("  ")# NB two spaces as some values contain a space
                    values = [v.strip() for v in split_values if v.strip()]

                # print("return_list", return_list)
                return {dict_list_key: return_list}

            line_index += 1

        return None