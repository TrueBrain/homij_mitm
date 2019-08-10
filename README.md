# Homij Forwarder

Homij offers monitoring of a modern house, by checking information from all kinds of equipment throughout the house.
For example: WTW, Boiler, Inverter, etc.
This information is collected on a Raspberry Pi, and sent to BaseN over https.
This man-in-the-middle server intercepts the https request to BaseN, and passes it along to BaseN.
In the meantime, it also tries to understand the request, and forwards it to InfluxDB.

In case you wonder how this could work, it is simply because all code explicitly ignores any certificate error.

## Installation

Run this Docker on a machine in the same subnet.
See `Configuration` section for more information for what settings to pass along.

Next, run these commands on the Raspberry Pi:

```bash
iptables -t nat -A OUTPUT -p tcp --dport 443 -j DNAT --to-destination <IP of this MITM server>:443
```

Now all https traffic is redirected to your MITM.
This also means you can monitor no other https traffic is being done.

## Certificate

You can get this in various of ways.
Most likely the easiest is to generate a self-signed.

```bash
openssl req -x509 -newkey rsa:4096 -keyout selfsigned.key -out selfsigned.cert -days 365
```

## Configuration

The `--help` shows all the possible commands. In short:

```
Options:
  --cert-file FILE         Certificate to use for SSL  [required]
  --key-file FILE          Private key of the certificate to use for SSL
                           [required]
  --log-folder DIRECTORY   Folder to log the raw requests in
  --basen-id TEXT          The ID of the BaseN to intercept  [required]
  --influxdb-host TEXT     Host of the InfluxDB server  [required]
  --influxdb-port INTEGER  Port of the InfluxDB server  [default: 8086]
  --influxdb-db TEXT       Database of the InfluxDB server  [default: db0]
  --port INTEGER           Port of the server  [default: 443]
  -h, --help               Show this message and exit.
```

## Testing

Fire up a curl command like (this is one of the stats that tells how long the system has been running; rather boring, but it is just as an example):

```bash
curl -k -d '{"id":"testing","content":{"password":"password","username":"username","c":[{"write":{"rows":[{"path":"power","time":"1565432461000","channels":[{"channel":"pulse_1","long":"1","comment":"","unit":"Counter32"},{"channel":"pulse_2","long":"1","comment":"","unit":"Counter32"},{"channel":"pulse_3","long":"374103","comment":"","unit":"Counter32"},{"channel":"pulse_4","long":"1","comment":"","unit":"Counter32"},{"channel":"pulse_5","long":"1","comment":"","unit":"Counter32"}]}]}}]}}}' --header 'Host: www.example.org' https://127.0.0.1:443/_ua/testing/
```

The `-k` is used here, as we are using a self-signed certificate.
The request returns a 404, as that is the response `https://www.example.org/_ua/testing/` returns.
Feel free to use any other URL to test this out with.

## FAQ

### How did you get in the Raspberry Pi?

I did not.
I simply shut it down, got the SD card out, opened it via a PC, and inserted a SSH public key.
Now you can simply SSH to the machine, and get root access that way.

### Why did you build this?

Homij for a long time did not give credentials to login to BaseN myself.
After they did, it turns out the information they supply is so poorly, it was of no use to me.
So, as a true ITer, I wrote this MITM to process the data myself.
In result, I now have pretty graphs of everything that is going on in my house.
