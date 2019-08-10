# Homij Forwarder

Homij offers monitoring of a modern house, by checking information from all kinds of equipment throughout the house.
For example: WTW, Boiler, Inverter, etc.
This information is collected on a Raspberry Pi, and sent to BaseN over HTTPS.
This man-in-the-middle server intercepts the HTTPS request to BaseN, and passes it along to BaseN.
In the meantime, it also tries to understand the request, and forwards it to InfluxDB.

In case you wonder how this could work, it is simply because all code explicitly ignores any certificate error.

## Installation

Run this Docker on a machine in the same subnet.
See `Configuration` section for more information for what settings to pass along.

Next, run these commands on the Raspberry Pi:

```bash
iptables -t nat -A OUTPUT -p tcp --dport 443 -j DNAT --to-destination <IP of this MITM server>:443
```

Now all HTTPS traffic is redirected to your MITM.
This also means you can monitor no other HTTPS traffic is being done.

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
  --cert-file FILE        Certificate to use for SSL  [required]
  --key-file FILE         Private key of the certificate to use for SSL
                          [required]
  --log-folder DIRECTORY  Folder to log the raw requests in
  --basen-id TEXT         The ID of the BaseN to intercept  [required]
  --influxdb-url TEXT     URL of the InfluxDB server  [required]
  --influxdb-token TEXT   Token to access the InfluxDB server  [required]
  --influxdb-org TEXT     Organisation of the InfluxDB server  [required]
  --influxdb-bucket TEXT  Bucket to use in the InfluxDB server  [default:
                          metrics]
  --port INTEGER          Port of the server  [default: 443]
  -h, --help              Show this message and exit.
```

## Testing

Fire up a curl command like (this is one of the stats that tells how long the system has been running; rather boring, but it is just as an example):

```bash
curl -k -d '{"id":"testing","content":{"password":"password","username":"username","c":[{"write":{"rows":[{"path":"dsmr","time":"1628513892000","channels":[{"channel":"power","double":"0.0","comment":"","unit":"kW"},{"channel":"energy_low","double":"7237.292","comment":"","unit":"kWh"},{"channel":"energy_high","double":"3865.991","comment":"","unit":"kWh"},{"channel":"energy_low_prod","double":"5334.853","comment":"","unit":"kWh"},{"channel":"energy_high_prod","double":"12597.142","comment":"","unit":"kWh"},{"channel":"tariff","double":"2.0","comment":"","unit":""},{"channel":"power_prod","double":"1.234","comment":"","unit":"kW"}]}]}}]}}}' --header 'Host: www.example.org' https://127.0.0.1:443/_ua/testing/
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
