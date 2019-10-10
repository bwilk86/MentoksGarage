#Mentok's Home Automation

##Usage

All responses will have the form
```json
{
    "data": "Mixed type holding the content of the response",
    "message": "Description of what happened"
}

Responses will only detail the value of the `data field`

###Get state of Garage Door

**Definition**

`GET /api/door/`

**Response**
`200 OK` on success

```json
{
    {
        "identifier": "<GUID>",
        "name": "Garage Door",
        "state": "<open|closed>"
    }
}

###Open/Close Garage door

**Definition**

`POST|PUT /api/door`

**Arguments**

 - `"action": string<open|close>` action to perform (open or close door)

**Response**
`200 OK` on success
```json
{
    {
        "identifier": "<GUID>",
        "name": "Garage Door",
        "state": "<open|closed>"
    }
}

###Get state of Garage Lights

**Definition**

`GET /api/lights/`

**Response**
`200 OK` on success

```json
{
    {
        "identifier": "<GUID>",
        "name": "Garage Lights",
        "state": "<on|off>"
    }
}

###Turn On/Off Garage Lights

**Definition**

`POST|PUT /api/lights`

**Arguments**

 - `"action": string<on|off>` action to perform (turn lights on/off)

**Response**
`200 OK` on success
```json
{
    {
        "identifier": "<GUID>",
        "name": "Garage Lights",
        "state": "<on|off>"
    }
}
