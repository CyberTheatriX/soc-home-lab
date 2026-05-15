#!/usr/bin/env python3
"""
Playbook 1 — IP Blocker
Automatically blocks attacker IPs using iptables
"""

import subprocess
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

log = logging.getLogger(__name__)

# Track blocked IPs in memory to avoid duplicate blocks
blocked_ips = set()


def is_already_blocked(ip):
    """Check if IP is already in iptables."""
    try:
        result = subprocess.run(
            ["sudo", "iptables", "-L", "INPUT", "-n"],
            capture_output=True, text=True
        )
        return ip in result.stdout
    except Exception as e:
        log.error(f"Error checking iptables: {e}")
        return False


def block_ip(ip, reason="", source=""):
    """Block an IP using iptables."""

    # Skip whitelisted IPs
    if ip in config.WHITELIST:
        return

    # Skip if already blocked
    if ip in blocked_ips:
        return

    if is_already_blocked(ip):
        blocked_ips.add(ip)
        return

    try:
        subprocess.run(
            ["sudo", "iptables", "-I", "INPUT", "-s", ip, "-j", "DROP"],
            check=True, capture_output=True
        )
        blocked_ips.add(ip)
        log.warning(
            f"BLOCKED IP: {ip} | Source: {source} | Reason: {reason}"
        )
    except subprocess.CalledProcessError as e:
        log.error(f"Failed to block IP {ip}: {e}")
