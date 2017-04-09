
#!/usr/bin/python -tt

# Copyright (c) 2014, John Morrissey <jwm@horde.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#	* Redistributions of source code must retain the above copyright notice,
#	  this list of conditions and the following disclaimer.
#	* Redistributions in binary form must reproduce the above copyright
#	  notice, this list of conditions and the following disclaimer in the
#	  documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#import re

import errbot
import nagcgi
#import rt

class NagiosBot(errbot.BotPlugin):
	min_err_version = "2.0.0"
	max_err_version = "2.0.0"

	nagios = None

	def get_configuration_template(self):
		return {
			"NAGIOS_URL": "",
			"NAGIOS_USERNAME": "",
			"NAGIOS_PASSWORD": "",
		}

	def check_configuration(self, config):
		if type(config) != dict:
			raise Exception("Configuration must be a dict.")

		if "NAGIOS_URL" not in config:
			raise Exception("NAGIOS_URL must be specified.")
		if "NAGIOS_USERNAME" not in config:
			raise Exception("NAGIOS_USERNAME must be specified.")
		if "NAGIOS_PASSWORD" not in config:
			raise Exception("NAGIOS_PASSWORD must be specified.")

		self.nagios = nagcgi.Nagcgi(
			config["NAGIOS_URL"],
			config["NAGIOS_USERNAME"],
			config["NAGIOS_PASSWORD"])

		super(NagiosBot, self).configure(config)

	def activate(self):
		super(NagiosBot, self).activate()

	def ack_host_or_service(self, host, service, comment, who):
		if service:
			self.nagios.ack_svc_problem(
				host, service, comment, author=who)
		else:
			self.nagios.ack_host_problem(host, comment, author=who)

	@errbot.botcmd
	def nagios_ack(self, msg, args):
		args = args.strip()

		if args.startswith(("'", '"')):
			# The host and service name are quoted, so the
			# service name can contain spaces.
			delim = args[0]
			host_and_service = args[1:args.index(delim, 1)]
			reason = args[args.index(delim, 1) + 1:].strip()
		else:
			host_and_service, reason = args.split(" ", 1)

		if ":" in host_and_service:
			host, service = host_and_service.split(":")
		else:
			host, service = host_and_service, None

		self.ack_host_or_service(
			host, service, "%s (%s)" % (
				" ".join(args[1:]),
				errbot.backends.base.Message.frm(msg),
			),
			errbot.backends.base.Message.frm(msg))

		if service:
			return "Acked %s on %s." % (service, host)
		return "Acked %s." % host

	@errbot.botcmd
	def nagios_recheck(self, msg, args):
		host, service = args.split(":", 1)
		self.nagios.schedule_svc_check(host, service)
		return "Submitted recheck for %s on %s." % (service, host)

