# Known Activity Actions

## doorclosed
```
{
  "entities": {
    "device": "<deviceId>",
    "callingUser": "deleted",
    "otherUser": "deleted",
    "house": "<houseId>",
    "activity": "<activityId>"
  },
  "house": {
    "houseID": "<houseId>",
    "houseName": "<houseName>"
  },
  "dateTime": <epochTimestamp>,
  "action": "doorclosed",
  "deviceName": "<deviceName>",
  "deviceID": "<deviceId>",
  "deviceType": "lock",
  "callingUser": {
    "UserID": "deleted",
    "FirstName": "Unknown",
    "LastName": "User",
    "UserName": "deleteduser",
    "PhoneNo": "deleted"
  },
  "otherUser": {
    "UserID": "deleted",
    "FirstName": "Unknown",
    "LastName": "User",
    "UserName": "deleteduser",
    "PhoneNo": "deleted"
  },
  "info": {
    "DateLogActionID": "<uniqueId>"
  }
}
```
## dooropen

```
{
  "entities": {
    "device": "<deviceId>",
    "callingUser": "deleted",
    "otherUser": "deleted",
    "house": "<houseId>",
    "activity": "<activityId>"
  },
  "house": {
    "houseID": "<houseId>",
    "houseName": <houseName>
  },
  "dateTime": <epochTimestamp>,
  "action": "dooropen",
  "deviceName": <deviceName>,
  "deviceID": "<deviceId>",
  "deviceType": "lock",
  "callingUser": {
    "UserID": "deleted",
    "FirstName": "Unknown",
    "LastName": "User",
    "UserName": "deleteduser",
    "PhoneNo": "deleted"
  },
  "otherUser": {
    "UserID": "deleted",
    "FirstName": "Unknown",
    "LastName": "User",
    "UserName": "deleteduser",
    "PhoneNo": "deleted"
  },
  "info": {
    "DateLogActionID": "<uniqueId>"
  }
}
```

## unlock

```
{
  "entities": {
    "device": "<deviceId>",
    "callingUser": "<userId>",
    "otherUser": "deleted",
    "house": "<houseId>",
    "activity": "<activityId>"
  },
  "house": {
    "houseID": "<houseId>",
    "houseName": <houseName>
  },
  "source": {
    "sourceType": "mercury"
  },
  "dateTime": <epochTimestamp>,
  "action": "unlock",
  "deviceName": <deviceName>,
  "deviceID": "<deviceId>",
  "deviceType": "lock",
  "callingUser": {
    "UserID": "<userId>",
    "FirstName": "<firstName>",
    "LastName": "<lastName>",
    "imageInfo": {
      "original": {
        "width": <imageWidth>,
        "height": <imageHeight>,
        "format": "<imageFormat>",
        "url": "<imageUrl>",
        "secure_url": "<imageSecureUrl>"
      },
      "thumbnail": {
        "width": <thumbnailWidth>,
        "height": <thumbnailHeight>,
        "format": "<imageFormat>",
        "url": "<thumbnailUrl>",
        "secure_url": "<thumbnailSecureUrl>"
      }
    }
  },
  "otherUser": {
    "UserID": "deleted",
    "FirstName": "Unknown",
    "LastName": "User",
    "UserName": "deleteduser",
    "PhoneNo": "deleted"
  },
  "info": {
    "agent": "mercury",
    "keypad": true
  }
}
```

## lock

```
{
  "entities": {
    "device": "<deviceId>",
    "callingUser": "<userId>",
    "otherUser": "deleted",
    "house": "<houseId>",
    "activity": "<activityId>"
  },
  "house": {
    "houseID": "<houseId>",
    "houseName": <houseName>
  },
  "dateTime": <epochTimestamp>,
  "action": "lock",
  "deviceName": <deviceName>,
  "deviceID": "<deviceId>",
  "deviceType": "lock",
  "callingUser": {
    "UserID": "<userId>",
    "FirstName": "<firstName>",
    "LastName": "<lastName>"
  },
  "otherUser": {
    "UserID": "deleted",
    "FirstName": "Unknown",
    "LastName": "User",
    "UserName": "deleteduser",
    "PhoneNo": "deleted"
  },
  "info": {
    "remote": true,
    "DateLogActionID": "<uniqueId>"
  }
}
```
## onetouchlock

```
{
  "entities": {
    "device": "<deviceId>",
    "callingUser": "deleted",
    "otherUser": "deleted",
    "house": "<houseId>",
    "activity": "<activityId>"
  },
  "house": {
    "houseID": "<houseId>",
    "houseName": <houseName>
  },
  "dateTime": <epochTimestamp>,
  "action": "onetouchlock",
  "deviceName": <deviceName>,
  "deviceID": "<deviceId>",
  "deviceType": "lock",
  "callingUser": {
    "UserID": "deleted",
    "FirstName": "Unknown",
    "LastName": "User",
    "UserName": "deleteduser",
    "PhoneNo": "deleted"
  },
  "otherUser": {
    "UserID": "deleted",
    "FirstName": "Unknown",
    "LastName": "User",
    "UserName": "deleteduser",
    "PhoneNo": "deleted"
  },
  "info": {
    "DateLogActionID": "<uniqueId>"
  }
}
```
