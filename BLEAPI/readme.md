### API csv file rules:

    Each line has 4 attributes: [idx],[API content],[API type],[API name]
        - idx: Sequence number staring from 1
        - API content: content of the message sent to the BLE peripheral device.
            - Sting
            - Byte array: will be split by ' '
                For example: 
                    if you want to sand out an array like this: 
                                0xFF,0xFF,0xFF,0xFF
                    this attribute in this csv file should be like:
                                255 255 255 255
        - API type
            - str
            - ba
        - API name
            - name of the APIs

        Examples can be find in the api.csv file
    
    The file needs to be stored in this path.