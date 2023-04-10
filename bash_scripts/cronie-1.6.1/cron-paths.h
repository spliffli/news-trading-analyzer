/* This file has been automatically generated.  Do not edit. */

#ifndef _CRON_PATHS_H_
#define _CRON_PATHS_H_

		/* SPOOLDIR is where the crontabs live.
		 * This directory will have its modtime updated
		 * whenever crontab(1) changes a crontab; this is
		 * the signal for cron(8) to look at each individual
		 * crontab file and reload those whose modtimes are
		 * newer than they were last time around (or which
		 * didn't exist last time around...)
		 * or it will be checked by inotify
		 */
#define SPOOL_DIR	"/usr/local/var/spool/cron"

		/* CRON_HOSTNAME is file in SPOOL_DIR which, if it
		 * exists, and does not just contain a line matching
		 * the name returned by gethostname(), causes all
		 * crontabs in SPOOL_DIR to be ignored.  This is
		 * intended to be used when clustering hosts sharing
		 * one NFS-mounted SPOOL_DIR, and where only one host
		 * should use the crontab files here at any one time.
		 */
#define CRON_HOSTNAME	".cron.hostname"

		/* cron allow/deny file.  At least cron.deny must
		 * exist for ordinary users to run crontab.
		 */
#define	CRON_ALLOW	"/usr/local/etc/cron.allow"
#define	CRON_DENY	"/usr/local/etc/cron.deny"

		/* directory of cron pid file */
#define CRON_PID_DIR "/usr/local/var/run"

		/* 4.3BSD-style crontab f.e. /etc/crontab */
#define SYSCRONTAB	"/usr/local/etc/crontab"

		/* system crontab dir f.e. /etc/cron.d/ */
#define SYS_CROND_DIR	"/usr/local/etc/cron.d"

#define SYSCONFDIR	"/usr/local/etc"

#endif /* _CRON_PATHS_H_ */
