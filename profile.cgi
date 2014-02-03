#!/usr/bin/perl -w
use strict;
use CGI::Carp qw(fatalsToBrowser); # �G���[���b�Z�[�W��\������i���Ȃ��ꍇ�R�����g�A�E�g�j
use CGI;
use CGI::Session;
use HTML::Template;
require './config.pl';
require './global.pl';
require './vars.pl';
require './jcode.pl';

my $cgi;
my %config;
my $msg;
my $session;
my $sid;

my $dbh;

#�v���O�����J�n
&main;

##########
# ���C��
sub main {
	$cgi = new CGI;
	$msg = '';

	# �ݒ�ǂݍ���
	%config = &config;

	# �Z�b�V�����ǂݍ���
	$session = &readSession(1);
	if (defined $session) {
		# �Z�b�V���� ID
		$sid = $session->id;

		# DB �I�[�v��
		$dbh = &connectDB(1);

		# ���݂̉��
		$msg .= &checkOnline($dbh, $session->param('userid'), '�v���t�B�[��');

		# ��ʕ\��
		&disp;

		# DB �N���[�Y
		&disconnectDB($dbh);
	}
}

###########
# ��ʕ\��
sub disp {
	# �e���v���[�g�ǂݍ���
	my $tmpl = &readTemplate($cgi);

	# ���ʃe���v���[�g�ϐ��Z�b�g
	$msg .= &setCommonVars($tmpl, $session, $dbh);

	my ($user, $realname, $birthday, $sex, $blood, $job, $part, $place, $age, $note, $lasttime, $useragent) = &getUserInfo();
	$birthday =~ s/-//g;
	if ($birthday eq '00000000') {
		$birthday = '';
	}
	
	# ���[�U�[��񂪎擾�ł��Ă���
	if ($user) {
	
		# ���b�Z�[�W�𑗂�
		if ($tmpl->query(name => 'URL_SENDMESSAGE') eq 'VAR') {
			if ($cgi->param('userid') && $session->param('userid') != $cgi->param('userid')) {
				my $url = 'sendmessage.cgi?receiver_userid='.$cgi->param('userid');
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$tmpl->param(URL_SENDMESSAGE => &convertOutput($url));
			}
		}
		# �v���t�B�[���ύX�� URL
		if ($tmpl->query(name => 'URL_EDITPROFILE') eq 'VAR') {
			if ($session->param('powerlevel') >= 5 || !$cgi->param('userid') || $session->param('userid') == $cgi->param('userid')) {
				my $userid = $cgi->param('userid') || $session->param('userid');
				my $url = 'editprofile.cgi?userid='.$userid;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$tmpl->param(URL_EDITPROFILE => &convertOutput($url));
			}
		}

		# ���[�U�[��
		if ($tmpl->query(name => 'USER') eq 'VAR') {
			$tmpl->param(USER => &convertOutput($user));
		}
		# �{��
		if ($tmpl->query(name => 'REALNAME') eq 'VAR') {
			$tmpl->param(REALNAME => &convertOutput($realname));
		}
		# �a����
		if ($tmpl->query(name => 'BIRTHDAY') eq 'VAR') {
			if ($birthday =~ /(....)(..)(..)/) {
				my $b = "$1-$2-$3";
				$tmpl->param(BIRTHDAY => &convertOutput($b));
			}
		}
		# ����
		if ($tmpl->query(name => 'SEX') eq 'VAR') {
			if ($sex eq 'M') {
				$tmpl->param(SEX => '�j��');
			} elsif ($sex eq 'F') {
				$tmpl->param(SEX => '����');
			}
		}
		# ���t�^
		if ($tmpl->query(name => 'BLOOD') eq 'VAR') {
			if ($blood eq 'A') {
				$tmpl->param(BLOOD => 'A�^');
			} elsif ($blood eq 'B') {
				$tmpl->param(BLOOD => 'B�^');
			} elsif ($blood eq 'O') {
				$tmpl->param(BLOOD => 'O�^');
			} elsif ($blood eq 'AB') {
				$tmpl->param(BLOOD => 'AB�^');
			}
		}
		# �E��
		if ($tmpl->query(name => 'JOB') eq 'VAR') {
			$tmpl->param(JOB => &convertOutput($job));
		}
		# �y��
		if ($tmpl->query(name => 'PART') eq 'VAR') {
			$tmpl->param(PART => &convertOutput($part));
		}
		# �Z��
		if ($tmpl->query(name => 'PLACE') eq 'VAR') {
			$tmpl->param(PLACE => &convertOutput($place));
		}

		# ��
		if ($tmpl->query(name => 'AGE') eq 'VAR') {
			if ($age) {
				my ($now_sec,$now_min,$now_hour,$now_mday,$now_month,$now_year,$now_wday,$now_stime) = localtime(time());
				$now_year = $now_year + 1900;
				$now_month++;
				my $year = $age + 1976;
				my $class = $now_year - $year + 3;
				if ($now_month >= 4) {
					$class++;
				}
				if ($class > 3) {
					$tmpl->param(AGE => $age.'��'.$year.'�N����');
				} else {
					$tmpl->param(AGE => $age.'��'.$class.'�N��');
				}
			}
		}

		# ���ȏЉ�
		if ($tmpl->query(name => 'NOTE') eq 'VAR') {
			$tmpl->param(NOTE => &convertOutput($note, 1));
		}

		# �Ǘ��җp
		if ($session->param('powerlevel') >= 5) {
			# �ŏI���O�C������
			if ($tmpl->query(name => 'LASTTIME') eq 'VAR') {
				$tmpl->param(LASTTIME => &convertOutput($lasttime));
			}

			# �ŏI���[�U�[�G�[�W�F���g
			if ($tmpl->query(name => 'USERAGENT') eq 'VAR') {
				$tmpl->param(USERAGENT => &convertOutput($useragent));
			}
		}
	}
	
	# ���b�Z�[�W�i����΁j
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

########################
# ���݂̃��[�U�[���擾
sub getUserInfo() {
	my $userid = $cgi->param('userid') || $session->param('userid');
	my @bind = ($userid, '0');
	my @users = &selectFetchArray($dbh, 'SELECT name, realname, birthday, sex, blood, job, part, place, age, note, lasttime, useragent FROM users WHERE userid=? and deleteflag=?', @bind);
	if (@users) {
		return @users;
	} else {
		$msg .= '���[�U�[��񂪎擾�ł��܂���ł����B';
		return 0;
	}
}


