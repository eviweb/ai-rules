# Infrastructure examples

Instrument each hop once, read the result, then decide where to dig. Replace names by the real ones.

## DNS

- Ask the resolver in use and the authoritative server separately: `dig example.org`, `dig @1.1.1.1 example.org`, `dig +trace example.org`. A difference points at caching or a wrong record.
- Check what the host really uses: `resolvectl status`, `/etc/resolv.conf`, `getent hosts example.org` (what applications see, unlike `dig`).
- Check the TTL before assuming a change has propagated.

## Reverse proxy and HTTP

- Follow the request hop by hop: `curl -v` against the proxy, then directly against the upstream, comparing status, headers (`Host`, `X-Forwarded-*`, `Location`) and body.
- Validate the configuration before reloading: `nginx -t`, `haproxy -c -f <file>`, `postfix check`.
- Read both access and error logs of each hop at the time of the failing request; note the request id if there is one.

## Containers

- `docker logs <name>` (or the runtime equivalent) first; then `docker inspect` for the effective environment, mounts, ports and healthcheck.
- Compare the image configuration with the running one: a changed file on the host is not in the container unless it is mounted or the image was rebuilt.
- `docker exec <name> env` and a shell inside show what the process sees, not what the compose file says.

## Services and hosts

- `systemctl status <unit>` then `journalctl -u <unit> --since "10 min ago"`.
- Permissions, disk space, clock and open ports: `ls -l`, `df -h`, `date`, `ss -ltnp`.

## CI

- Reproduce the failing step locally with the same command and environment variables.
- Diff what differs between a passing and a failing run: runner image, dependency versions, secrets availability, working directory, cache.
- Print the value that is suspected (never a secret: print whether it is set and its length).
