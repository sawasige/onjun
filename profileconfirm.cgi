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
my $userid = 0;
my @ages = ();

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
		
		# �C�����郆�[�U�[ID
		if ($session->param('powerlevel') >= 5) {
			$userid = $cgi->param('userid') || $session->param('userid');
		} else {
			$userid = $session->param('userid');
		}

		# �L�����Z���Ȃ�߂�
		if ($cgi->param('cancel')) {
			# ��ʃ��_�C���N�g
			my $url = 'editprofile.cgi?userid='.$userid;
			if (&isMobile()) {
				$url .= '&'.$config{'sessionname'}.'='.$sid;
			}
			print $cgi->redirect($url);
		} else {
			# DB �I�[�v��
			$dbh = &connectDB(1);

			# �o�^
			my $check = 0;
			if ($cgi->param('submit')) {
				$check = &regUser();
			}

			# ��ʕ\��
			if (!$check) {
				# ���݂̉��
				$msg .= &checkOnline($dbh, $session->param('userid'), '�v���t�B�[���C���m�F');

				&disp;
			}
			
			# DB �N���[�Y
			&disconnectDB($dbh);
		}
	}
	
}

###########
# ��ʕ\��
sub disp {
	# �e���v���[�g�ǂݍ���
	my $tmpl = &readTemplate($cgi);

	# ���ʃe���v���[�g�ϐ��Z�b�g
	$msg .= &setCommonVars($tmpl, $session, $dbh);

	my $user = $session->param('user');
	my $pass = $session->param('pass');
	my $mail = $session->param('mail');
	my $realname = $session->param('realname');
	my $birthday = $session->param('birthday');
	my $sex = $session->param('sex');
	my $blood = $session->param('blood');
	my $job = $session->param('job');
	my $part = $session->param('part');
	my $place = $session->param('place');
	my $age = $session->param('age');
	my $note = $session->param('note');

	if ($user) {

		# ���[�U�[ID
		if ($tmpl->query(name => 'USERID') eq 'VAR') {
			$tmpl->param(USERID => $userid);
		}
		# ���[�U�[��
		if ($tmpl->query(name => 'USER') eq 'VAR') {
			$tmpl->param(USER => &convertOutput($user));
		}
		# �p�X���[�h
		if ($tmpl->query(name => 'PASS') eq 'VAR') {
			$tmpl->param(PASS => &convertOutput($pass));
		}
		# ���[��
		if ($tmpl->query(name => 'MAIL') eq 'VAR') {
			$tmpl->param(MAIL => &convertOutput($mail));
		}
		# �{��
		if ($tmpl->query(name => 'REALNAME') eq 'VAR') {
			$tmpl->param(REALNAME => &convertOutput($realname));
		}
		# �a����
		if ($tmpl->query(name => 'BIRTHDAY') eq 'VAR') {
			$tmpl->param(BIRTHDAY => &convertOutput($birthday));
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
	} else {
		$msg .= '�C�����̏�񂪎����܂����B';
	}
	
	# ���b�Z�[�W�i����΁j
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

################
# �I�����ڎ擾
sub getValues() {
	# ��
	@ages = ();
	my ($now_sec,$now_min,$now_hour,$now_mday,$now_month,$now_year,$now_wday,$now_stime) = localtime(time());
	$now_year = $now_year + 1900;
	$now_month++;
	for (my $i = $now_year - 1976 + 3; $i >= 1; $i--) {
		my $year = $i + 1976;
		my $class = $now_year - $year + 3;
		if ($now_month >= 4) {
			$class++;
		}
		my $age;
		if ($class > 3) {
			$age = [$i, $i.'��'.$year.'�N����'];
		} else {
			$age = [$i, $i.'��'.$class.'�N��'];
		}
		if ($class > 0) {
			push(@ages, $age);
		}
	}
}


################
# ���[�U�[�o�^
sub regUser() {
	my $user = $session->param('user');
	my $pass = $session->param('pass');
	my $mail = $session->param('mail');
	my $realname = $session->param('realname');
	my $birthday = $session->param('birthday');
	my $sex = $session->param('sex');
	my $blood = $session->param('blood');
	my $job = $session->param('job');
	my $part = $session->param('part');
	my $place = $session->param('place');
	my $age = $session->param('age');
	my $note = $session->param('note');

	# �d���`�F�b�N
	my @bind = ($userid, $user, '0');
	my $count = &selectFetch($dbh, 'SELECT count(*) FROM users WHERE userid!=? AND name=? AND deleteflag=?', @bind);
	if ($count) {
		$msg .= '���ɓ������[�U�[�����g���Ă��܂��B';
		return 0;
	}

	# DB �o�^
	my @bind = ($user, $pass, $mail, $realname, $birthday, $sex, $blood, $job, $part, $place, $age, $note, $userid);
	my $sql = 
		'UPDATE users SET '.
		'name = ?, '.
		'pass = ?, '.
		'mail = ?, '.
		'realname = ?, '.
		'birthday = ?, '.
		'sex = ?, '.
		'blood = ?, '.
		'job = ?, '.
		'part = ?, '.
		'place = ?, '.
		'age = ?, '.
		'note = ? '.
		'where userid = ?';
	&doDB($dbh, $sql, @bind);

	$msg .= '�v���t�B�[�����C�����܂����B';
	$session->clear(['user', 'pass', 'mail', 'realname', 'birthday', 'sex', 'blood', 'job', 'part', 'place', 'age', 'note']);
	$session->param('msg', $msg);
	$session->flush();

	
	# ��ʃ��_�C���N�g
	if (&isMobile()) {
		# �Z�b�V������ URL ���ߍ���
		print $cgi->redirect("alert.cgi?$config{'sessionname'}=$sid");
	} else {
		# �Z�b�V������ Cookie ���ߍ��܂�Ă���
		print $cgi->redirect('alert.cgi');
	}

	return 1;
}

