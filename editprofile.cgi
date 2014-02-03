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

		# DB �I�[�v��
		$dbh = &connectDB(1);

		# �ύX���郆�[�U�[ID
		if ($session->param('powerlevel') >= 5) {
			$userid = $cgi->param('userid') || $session->param('userid');
		} else {
			$userid = $session->param('userid');
		}

		# �o�^
		my $check = 0;
		if ($cgi->param('submit')) {
			$check = &regUser();
		}

		# �I�����ڎ擾
		&getValues();

		# ��ʕ\��
		if (!$check) {
			# ���݂̉��
			$msg .= &checkOnline($dbh, $session->param('userid'), '�v���t�B�[���C��');

			&disp;
		}

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

	my $user;
	my $pass;
	my $mail;
	my $realname;
	my $birthday;
	my $sex;
	my $blood;
	my $job;
	my $part;
	my $place;
	my $age;
	my $note;
	
	if ($cgi->param('submit')) {
		$user = $cgi->param('user');
		$pass = $cgi->param('pass');
		$mail = $cgi->param('mail');
		$realname = $cgi->param('realname');
		$birthday = $cgi->param('birthday');
		$sex = $cgi->param('sex');
		$blood = $cgi->param('blood');
		$job = $cgi->param('job');
		$part = $cgi->param('part');
		$place = $cgi->param('place');
		$age = $cgi->param('age');
		$note = $cgi->param('note');
	} elsif ($session->param('changeprofile')) {
		$session->clear(['changeprofile']);
		$session->flush();
		$user = $session->param('user');
		$pass = $session->param('pass');
		$mail = $session->param('mail');
		$realname = $session->param('realname');
		$birthday = $session->param('birthday');
		$sex = $session->param('sex');
		$blood = $session->param('blood');
		$job = $session->param('job');
		$part = $session->param('part');
		$place = $session->param('place');
		$age = $session->param('age');
		$note = $session->param('note');
	} else {
		my @userInfo = &getUserInfo();
		$user = $userInfo[0];
		$pass = $userInfo[1];
		$mail = $userInfo[2];
		$realname = $userInfo[3];
		$birthday = $userInfo[4];
		$sex = $userInfo[5];
		$blood = $userInfo[6];
		$job = $userInfo[7];
		$part = $userInfo[8];
		$place = $userInfo[9];
		$age = $userInfo[10];
		$note = $userInfo[11];
		$birthday =~ s/-//g;
		if ($birthday eq '00000000') {
			$birthday = '';
		}
	}

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
	if ($tmpl->query(name => 'SEX') eq 'LOOP') {
		$tmpl->param(SEX => [
			{
				SEXVALUE => '',
				SEXSELECTED => $sex eq '' && 'selected',
				SEXLABEL => '���I��'
			},
			{
				SEXVALUE => 'M',
				SEXSELECTED => $sex eq 'M' && 'selected',
				SEXLABEL => '�j��'
			},
			{
				SEXVALUE => 'F',
				SEXSELECTED => $sex eq 'F' && 'selected',
				SEXLABEL => '����'
			}
		]);
	}
	# ���t�^
	if ($tmpl->query(name => 'BLOOD') eq 'LOOP') {
		$tmpl->param(BLOOD => [
			{
				BLOODVALUE => '',
				BLOODSELECTED => $blood eq '' && 'selected',
				BLOODLABEL => '���I��'
			},
			{
				BLOODVALUE => 'A',
				BLOODSELECTED => $blood eq 'a' && 'selected',
				BLOODLABEL => 'A�^'
			},
			{
				BLOODVALUE => 'B',
				BLOODSELECTED => $blood eq 'B' && 'selected',
				BLOODLABEL => 'B�^'
			},
			{
				BLOODVALUE => 'O',
				BLOODSELECTED => $blood eq 'O' && 'selected',
				BLOODLABEL => 'O�^'
			},
			{
				BLOODVALUE => 'AB',
				BLOODSELECTED => $blood eq 'AB' && 'selected',
				BLOODLABEL => 'AB�^'
			}
		]);
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
	if ($tmpl->query(name => 'AGE') eq 'LOOP') {
		my %age;
		$age{AGEVALUE} = '';
		$age{AGESELECTED} = $age eq '' && 'selected';
		$age{AGELABEL} = '���I��';
		my @agedata = ();
		push(@agedata, \%age);
		foreach my $row(@ages) {
			my ($ageid, $name) = @$row;
			my %age;
			$age{AGEVALUE} = $ageid;
			$age{AGESELECTED} = $age eq $ageid && 'selected';
			$age{AGELABEL} = $name;
			push(@agedata, \%age);
		}
		$tmpl->param(AGE => \@agedata);
	}

	# ���ȏЉ�
	if ($tmpl->query(name => 'NOTE') eq 'VAR') {
		$tmpl->param(NOTE => &convertOutput($note));
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

####################
# ���[�U�[���擾
sub getUserInfo() {
	my @bind = ($userid, '0');
	my @users = &selectFetchArray($dbh, 'SELECT name, pass, mail, realname, birthday, sex, blood, job, part, place, age, note FROM users WHERE userid=? and deleteflag=?', @bind);
	if (@users) {
		return @users;
	}
}

###############
# ���̓`�F�b�N
sub regUser() {
	$session->param('changeprofile', 1);
	$session->flush();

	if ($msg) {
		return 0;
	}

	# ���[�U�[��
	my $user = $cgi->param('user');
	$msg .= &checkString('���[�U�[��', $user, 30, 1);
	if ($msg) {
		return 0;
	}
	if ($user =~ /[\<\>\r\n]/) {
		$msg .= '���[�U�[���Ɏg�p�ł��Ȃ�����������܂��B';
		return 0;
	}

	# �p�X���[�h
	my $pass = $cgi->param('pass');
	$msg .= &checkString('�p�X���[�h', $pass, 30, 1);
	if ($msg) {
		return 0;
	}

	# ���[��
	my $mail = $cgi->param('mail');
	$msg .= &checkString('���[��', $mail, 60, 1);
	if ($msg) {
		return 0;
	}
	if ($mail !~ /^[\x01-\x7F]+@(([-a-z0-9]+\.)*[a-z]+|\[\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\])/) {
		$msg .= '���肦�Ȃ����[���A�h���X�����͂���Ă��܂��B';
		return 0;
	}
	
	# �{��
	my $realname = $cgi->param('realname');
	$msg .= &checkString('�{��', $realname, 60, 0);
	if ($msg) {
		return 0;
	}
	if ($realname =~ /[\<\>\r\n]/) {
		$msg .= '�{���Ɏg�p�ł��Ȃ�����������܂��B';
		return 0;
	}

	# �a����
	my $birthday = $cgi->param('birthday');
	$msg .= &checkDateString('�a����', $birthday, 0);
	if ($msg) {
		return 0;
	}

	# ����
	my $sex = $cgi->param('sex');
	if ($sex && $sex ne 'M' && $sex ne 'F') {
		$msg .= '���ʂ̒l���s���ł��B';
		return 0;
	}

	# ���t�^
	my $blood = $cgi->param('blood');
	if ($blood && $blood ne 'A' && $blood ne 'B' && $blood ne 'O' && $blood ne 'AB') {
		$msg .= '���t�^�̒l���s���ł��B';
		return 0;
	}

	# �E��
	my $job = $cgi->param('job');
	$msg .= &checkString('�E��', $job, 60, 0);
	if ($msg) {
		return 0;
	}
	if ($job =~ /[\<\>\r\n]/) {
		$msg .= '�E�ƂɎg�p�ł��Ȃ�����������܂��B';
		return 0;
	}

	# �y��
	my $part = $cgi->param('part');
	$msg .= &checkString('�p�[�g', $part, 60, 0);
	if ($msg) {
		return 0;
	}
	if ($part =~ /[\<\>\r\n]/) {
		$msg .= '�y��Ɏg�p�ł��Ȃ�����������܂��B';
		return 0;
	}

	# �Z��
	my $place = $cgi->param('place');
	$msg .= &checkString('�p�[�g', $place, 60, 0);
	if ($msg) {
		return 0;
	}
	if ($place =~ /[\<\>\r\n]/) {
		$msg .= '�Z���Ɏg�p�ł��Ȃ�����������܂��B';
		return 0;
	}

	# ��
	my $age = $cgi->param('age');
	my ($now_sec,$now_min,$now_hour,$now_mday,$now_month,$now_year,$now_wday,$now_stime) = localtime(time());
	$now_year = $now_year + 1900;
	$now_month++;
	my $max_age = $now_year - 1976 + 3;
	if ($now_month >= 4) {
		$max_age ++;
	}
	if ($age && ($age < 1 || $age >= $max_age)) {
		$msg .= '���̒l���s���ł��B'.$age;
		return 0;
	}

	# ���ȏЉ�
	my $note = $cgi->param('note');
	$msg .= &checkString('���ȏЉ�', $note, 400, 0);
	if ($msg) {
		return 0;
	}

	# �d���`�F�b�N
	my @bind = ($userid, $user, '0');
	my $count = &selectFetch($dbh, 'SELECT count(*) FROM users WHERE userid!=? AND name=? AND deleteflag=?', @bind);
	if ($count) {
		$msg .= '���ɓ������[�U�[�����g���Ă��܂��B';
		return 0;
	}
	
	
	# ���̓`�F�b�N�����I�I

	$session->param('user', $user);
	$session->param('pass', $pass);
	$session->param('mail', $mail);
	$session->param('realname', $realname);
	$session->param('birthday', $birthday);
	$session->param('sex', $sex);
	$session->param('blood', $blood);
	$session->param('job', $job);
	$session->param('part', $part);
	$session->param('place', $place);
	$session->param('age', $age);
	$session->param('note', $note);
	$session->flush();
	# ��ʃ��_�C���N�g
	my $url = 'profileconfirm.cgi?userid='.$userid;
	if (&isMobile()) {
		$url .= '&'.$config{'sessionname'}.'='.$sid;
	}
	print $cgi->redirect($url);

	return 1;
}

