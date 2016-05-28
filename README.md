# ssh-hecate

Hecate simlifies the task of distributing ssh public keys in a network.  Hecate uses [Consul](https://www.consul.io/) as a persistent store for a user's public keys and removes the need for users to push their public keys around the network.  From a user perspective, the process is simple:

1. Run `hecate provision` to generate a SSH private/public key pair.  The public key is uploaded to Consul.  The private key never leaves the host.
2. Wait.  Remote hosts running the Hecate daemon will periodically connect to Consul and generate a `~/.ssh/authorized_keys` file for each user that:
  1. Has an account on the remote host AND
  2. Has keys distributed via Hecate
3. SSH to the remote host... no password needed!

## Installation
### Install Dependencies
### Install Hecate
### Configure Hecate
### Provision a Key
### Run the Daemon

## Hecate Commands
Hecate contains several sub-commands
* [`provision`](https://github.com/ncfritz/ssh-hecate/wiki/provision) - seeds a public key to Consul, creating a private/public key pair is necessary
* [`list`](https://github.com/ncfritz/ssh-hecate/wiki/list) - lists users in Consul, or the keys for a specific user
* [`get`](https://github.com/ncfritz/ssh-hecate/wiki/get) - retrieves the public key for a user/host combination
* [`delete`](https://github.com/ncfritz/ssh-hecate/wiki/delete) - deletes a user from Consul, or a specific key for a user
* [`sync`](https://github.com/ncfritz/ssh-hecate/wiki/sync) - synchronizes the `authorized_keys` for all, or a specific user/s
* [`config`](https://github.com/ncfritz/ssh-hecate/wiki/config) - displays or edits the Consul configuration
* [`daemon`](https://github.com/ncfritz/ssh-hecate/wiki/daemon) - runs the Hecate daemon

## Running the Daemon
You can run the daemon in the foreground using`hecate daemon` for debugging or testing purposes.  It is recommended that you run the synchronizing daemon as a managed, long lived process using [Supervisord](http://supervisord.org/).  Hecate ships with a sample Supervisord config file in `etc/supervisord.config`.  To run Supervisord locally use the following command:

```
sudo supervisord -c /usr/local/hecate/etc/supervisord.config 
```

Note that you need to run as root.  Since Hecate will be creating/modifying the `.ssh/authorized_keys` files for all users it need to run as a priviledged user.  You may also wish to [run Supervisord on startup](http://supervisord.org/running.html#running-supervisord-automatically-on-startup).
