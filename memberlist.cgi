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
my @ages = ();
my $usercount = 0;
my @users = ();

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
		$sid = $session->id;

		# DB �I�[�v��
		$dbh = &connectDB(1);

		# ����
		if ($cgi->param('submit') || !$cgi->param('search')) {
			&searchUser();
		}

		# �I�����ڎ擾
		&getValues();

		# ���݂̉��
		$msg .= &checkOnline($dbh, $session->param('userid'), '�����o�[�ꗗ');

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

	my $job = '';
	my $part = '';
	my $age = '';
	if ($cgi->param('submit')) {
		$job = $cgi->param('job');
		$part = $cgi->param('part');
		$age = $cgi->param('age');
#	} else {
#		$age = &getUserAge();
	}
	
	# ���b�Z�[�W
	$msg .= $session->param('msg');
	$session->clear(['msg']);
	$session->flush();

	# ������ URL
	if ($tmpl->query(name => 'URL_MEMBERSEARCH') eq 'VAR') {
		my $url = 'memberlist.cgi?search=1';
		if (&isMobile) {
			$url .= '&'.$config{'sessionname'}.'='.$session->id;
		}
		$tmpl->param(URL_MEMBERSEARCH => &convertOutput($url));
	}
	
	# �E��
	if ($tmpl->query(name => 'JOB') eq 'VAR') {
		$tmpl->param(JOB => &convertOutput($job));
	}
	# �p�[�g�i�y��j
	if ($tmpl->query(name => 'PART') eq 'VAR') {
		$tmpl->param(PART => &convertOutput($part));
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

	# �����o�[�ꗗ
	if (@users && $tmpl->query(name => 'MEMBERS') eq 'LOOP') {
		my @userdata = ();
		foreach my $row(@users) {
			my ($userid, $name, $job, $part, $age, $note, $registtime) = @$row;
			my %user;
			# �v���t�B�[�� URL
			if ($tmpl->query(name => ['MEMBERS', 'MEMBERURL']) eq 'VAR') {
				my $url = 'profile.cgi?userid='.$userid;
				# �Z�b�V����
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$user{'MEMBERURL'} = &convertOutput($url);
			}
			# ���[�U�[��
			if ($tmpl->query(name => ['MEMBERS', 'MEMBERNAME']) eq 'VAR') {
				$user{'MEMBERNAME'} = &convertOutput($name);
			}
			# �E��
			if ($tmpl->query(name => ['MEMBERS', 'MEMBERJOB']) eq 'VAR') {
				$user{'MEMBERJOB'} = &convertOutput($job);
			}
			# �y��
			if ($tmpl->query(name => ['MEMBERS', 'MEMBERPART']) eq 'VAR') {
				$user{'MEMBERPART'} = &convertOutput($part);
			}
			# ��
			if ($age && $tmpl->query(name => ['MEMBERS', 'MEMBERAGE']) eq 'VAR') {
				$user{'MEMBERAGE'} = &convertOutput(&getAgeString($age));
			}
			# ����
			if ($tmpl->query(name => ['MEMBERS', 'TIME']) eq 'VAR') {
				$user{'TIME'} = &convertOutput($registtime);
			}
			# ���t
			if ($tmpl->query(name => ['MEMBERS', 'DATE']) eq 'VAR') {
				if ($registtime =~ /^(\d{4})\-(\d{2})\-(\d{2}) /) {
					$user{'DATE'} = &convertOutput($2.'��'.$3.'��');
				}
			}
			push(@userdata, \%user);
		}
		$tmpl->param(MEMBERS => \@userdata);
	}

	# �O�y�[�W
	if ($cgi->param('start') > 0 && $tmpl->query(name => 'PREVPAGEURL') eq 'VAR') {
		my $url = $cgi->url(-relative=>1).'?';
		$url .= 'submit=1';
		# �J�n�s
		my $pagesize = $cgi->param('size') + 0;
		if (!$pagesize) {
			$pagesize = 10;
		}
		my $prevstart = $cgi->param('start') - $pagesize;
		if ($prevstart < 0) {
			$prevstart = 0;
		}
		$url .= '&start='.$prevstart;
		$url .= '&size='.$pagesize;
		$url .= &getCondUrl();
		$tmpl->param(PREVPAGEURL => &convertOutput($url));
	}

	# �O�y�[�W�ԍ�
	if ($cgi->param('start') > 0 && $tmpl->query(name => 'BACKPAGELOOP') eq 'LOOP') {
		my $pagesize = $cgi->param('size') + 0;
		if (!$pagesize) {
			$pagesize = 10;
		}
		my $start = $cgi->param('start') + 0;
		my $no = int($start / $pagesize) + 1;
		my $startno = 1;
		if ($no > 10) {
			$startno = $no - 10
		}
		my @pagedata = ();
		for (my $i = $startno; $i <= $no - 1; $i++) {
			my %page;
			my $url = $cgi->url(-relative=>1).'?';
			$url .= 'submit=1';
			# �J�n�s
			$url .= '&start='.($i-1) * $pagesize;
			$url .= '&size='.$pagesize;
			$url .= &getCondUrl();
			if ($tmpl->query(name => ['BACKPAGELOOP', 'BACKPAGEURL']) eq 'VAR') {
				$page{BACKPAGEURL} = &convertOutput($url);
			}
			if ($tmpl->query(name => ['BACKPAGELOOP', 'BACKPAGELABEL']) eq 'VAR') {
				$page{BACKPAGELABEL} = $i;
			}
			push(@pagedata, \%page);
		}
		$tmpl->param(BACKPAGELOOP => \@pagedata);
	}

	# ���y�[�W
	if (($cgi->param('start') + @users) < $usercount && $tmpl->query(name => 'NEXTPAGEURL') eq 'VAR') {
		my $url = $cgi->url(-relative=>1).'?';
		$url .= 'submit=1';
		# �J�n�s
		my $pagesize = $cgi->param('size') + 0;
		if (!$pagesize) {
			$pagesize = 10;
		}
		my $nextstart = $cgi->param('start') + $pagesize;
		$url .= '&start='.$nextstart;
		$url .= '&size='.$pagesize;
		$url .= &getCondUrl();
		$tmpl->param(NEXTPAGEURL => &convertOutput($url));
	}

	# ���y�[�W�ԍ�
	if (($cgi->param('start') + @users) < $usercount && $tmpl->query(name => 'FORWARDPAGELOOP') eq 'LOOP') {
		my $pagesize = $cgi->param('size') + 0;
		if (!$pagesize) {
			$pagesize = 10;
		}
		my $start = $cgi->param('start') + 0;
		my $no = int($start / $pagesize) + 1;
		my $maxno = int($usercount / $pagesize);
		if ($usercount % $pagesize) {
			$maxno++;
		}
		my @pagedata = ();
		for (my $i = $no + 1; $i <= $maxno; $i++) {
			my %page;
			my $url = $cgi->url(-relative=>1).'?';
			$url .= 'submit=1';
			# �J�n�s
			$url .= '&start='.($i-1) * $pagesize;
			$url .= '&size='.$pagesize;
			$url .= &getCondUrl();
			if ($tmpl->query(name => ['FORWARDPAGELOOP', 'FORWARDPAGEURL']) eq 'VAR') {
				$page{FORWARDPAGEURL} = &convertOutput($url);
			}
			if ($tmpl->query(name => ['FORWARDPAGELOOP', 'FORWARDPAGELABEL']) eq 'VAR') {
				$page{FORWARDPAGELABEL} = $i;
			}
			push(@pagedata, \%page);
			# 10 �y�[�W�ȏ�͈ړ��ł��Ȃ�
			if (@pagedata >= 10) {
				last;
			}
		}
		$tmpl->param(FORWARDPAGELOOP => \@pagedata);
	}

	# ���݃y�[�W
	if ($tmpl->query(name => 'NOWPAGENOLABEL') eq 'VAR') {
		my $pagesize = $cgi->param('size') + 0;
		if (!$pagesize) {
			$pagesize = 10;
		}
		# �y�[�W��������ꍇ�����\��
		if ($pagesize < $usercount) {
			my $start = $cgi->param('start') + 0;
			my $no = int($start / $pagesize) + 1;
			$tmpl->param(NOWPAGENOLABEL => $no);
		}
	}


	# ���b�Z�[�W�i����΁j
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

###########################
# ���������� URL �G���R�[�h
sub getCondUrl {
	my $url = '';
	# �Z�b�V����
	if (&isMobile) {
		$url .= '&'.$config{'sessionname'}.'='.$session->id;
	}
	# �E��
	if ($cgi->param('job')) {
		$url .= '&job='.&urlEncode($cgi->param('job'));
	}
	# �p�[�g�i�y��j
	if ($cgi->param('part')) {
		$url .= '&part='.&urlEncode($cgi->param('part'));
	}
	# ��
	if ($cgi->param('age')) {
		$url .= '&age='.&urlEncode($cgi->param('age'));
	}
	return $url;
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

########################
# ���݂̃��[�U�[���擾
sub getUserAge() {
	my @bind = ($session->param('userid'), '0');
	my $age = &selectFetch($dbh, 'SELECT age FROM users WHERE userid=? and deleteflag=?', @bind);
	return $age;
}

################
# ���̓`�F�b�N
sub searchUser() {
	if ($msg) {
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

	# �p�[�g
	my $part = $cgi->param('part');
	$msg .= &checkString('�p�[�g', $part, 60, 0);
	if ($msg) {
		return 0;
	}
	if ($part =~ /[\<\>\r\n]/) {
		$msg .= '�p�[�g�Ɏg�p�ł��Ȃ�����������܂��B';
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

	# �������s
	my $pagesize = $cgi->param('size') + 0;
	if (!$pagesize) {
		$pagesize = 10; # �f�t�H���g�T�C�Y
	}
	my $pagestart = $cgi->param('start') + 0;
	my @bind = ('0');
	my $sqlcount = 'SELECT count(*)';
	my $sql = 'SELECT userid, name, job, part, age, note, registtime';
	my $sqlwhere = ' FROM users WHERE deleteflag=?';
	if ($job) {
		$sqlwhere .= ' and job LIKE ?';
		push(@bind, '%'.$job.'%');
	}
	if ($part) {
		$sqlwhere .= ' AND part LIKE ?';
		push(@bind, '%'.$part.'%');
	}
	if ($age) {
		$sqlwhere .= ' AND age=?';
		push(@bind, $age);
	}
	$sqlcount .= $sqlwhere;
	$sql .= $sqlwhere.' ORDER BY registtime DESC';

	@users = ();
	$usercount = &selectFetch($dbh, $sqlcount, @bind);
	if ($usercount >= $pagesize) {
		$sql .= ' LIMIT '.$pagestart.', '.$pagesize;
	}
	@users = &selectFetchArrayRef($dbh, $sql, @bind);
	
	if (@users == 0) {
		$msg .= '�����o�[��������܂���B';
	}

	return 1;
}
