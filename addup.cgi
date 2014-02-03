#!/usr/bin/perl -w
use strict;
use CGI::Carp qw(fatalsToBrowser); # �G���[���b�Z�[�W��\������i���Ȃ��ꍇ�R�����g�A�E�g�j
use CGI;
use CGI::Session;
use HTML::Template;
require './config.pl';
require './global.pl';
require './vars.pl';
require './mail.pl';
require './jcode.pl';

my $cgi;
my %config;
my $msg;
my $session;
my $sid;

my $dbh;
my $usercount = 0;
my @users = ();
my $start = 0;
my $size = 10;

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
		$msg .= &checkOnline($dbh, $session->param('userid'), '�W�v');

		# �W�v�i���y�[�W����Ă�ꍇ�͏W�v���Ȃ��j
		if (!$cgi->param('start')) {
			&addup();
		}

		# �W�v���ʎ擾
		&getAddup();

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


	# �R�����g�ꗗ
	if (@users && $tmpl->query(name => 'USERS') eq 'LOOP') {
		my @uservars = ();
		my $userno = $start + 1;
		foreach my $row(@users) {
			my ($userid, $messagecount, $topiccount, $topiccommentcount, $name) = @$row;
			my %commentvar;
			# ���[�U�[�A��
			if ($tmpl->query(name => ['USERS', 'USERNO']) eq 'VAR') {
				$commentvar{'USERNO'} = &convertOutput($userno);
			}
			$userno++;
			# ���[�U�[ID
			if ($tmpl->query(name => ['USERS', 'USERID']) eq 'VAR') {
				$commentvar{'USERID'} = &convertOutput($userid);
			}
			# ���[�U�[��
			if ($tmpl->query(name => ['USERS', 'USERNAME']) eq 'VAR') {
				$commentvar{'USERNAME'} = &convertOutput($name);
			}
			# ���[�U�[URL
			if ($tmpl->query(name => ['USERS', 'USERURL']) eq 'VAR') {
				my $url = 'profile.cgi?userid='.$userid;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$commentvar{'USERURL'} = &convertOutput($url);
			}
			# ���b�Z�[�W��
			if ($tmpl->query(name => ['USERS', 'MESSAGECOUNT']) eq 'VAR') {
				$commentvar{'MESSAGECOUNT'} = &convertOutput($messagecount);
			}
			# �g�s�b�N��
			if ($tmpl->query(name => ['USERS', 'TOPICCOUNT']) eq 'VAR') {
				$commentvar{'TOPICCOUNT'} = &convertOutput($topiccount);
			}
			# �g�s�b�N�R�����g��
			if ($tmpl->query(name => ['USERS', 'TOPICCOMMENTCOUNT']) eq 'VAR') {
				$commentvar{'TOPICCOMMENTCOUNT'} = &convertOutput($topiccommentcount);
			}

			push(@uservars, \%commentvar);
		}
		$tmpl->param(USERS => \@uservars);
	}

	# �O�y�[�W
	if ($start > 0 && $tmpl->query(name => 'PREVPAGEURL') eq 'VAR') {
		my $prevstart = $start - $size;
		if ($prevstart < 0) {
			$prevstart = 0;
		}
		my $url = $cgi->url(-relative=>1);
		$url .= '?start='.$prevstart;
		$url .= '&size='.$size;
		$url .= &getCondUrl();
		$tmpl->param(PREVPAGEURL => &convertOutput($url));
	}

	# �O�y�[�W�ԍ�
	if ($start > 0 && $tmpl->query(name => 'BACKPAGELOOP') eq 'LOOP') {
		my $no = int($start / $size) + 1;
		# 9 �y�[�W�ȏ�͈ړ��ł��Ȃ�
		my $startno = $no - 9;
		if ($startno < 1) {
			$startno = 1;
		}
		my @pagedata = ();
		for (my $i = $startno; $i <= $no - 1; $i++) {
			my %page;
			my $url = $cgi->url(-relative=>1);
			$url .= '?start='.($i-1) * $size;
			$url .= '&size='.$size;
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
	if (($start + @users) < $usercount && $tmpl->query(name => 'NEXTPAGEURL') eq 'VAR') {
		my $nextstart = $start + $size;
		my $url = $cgi->url(-relative=>1);
		$url .= '?start='.$nextstart;
		$url .= '&size='.$size;
		$url .= &getCondUrl();
		$tmpl->param(NEXTPAGEURL => &convertOutput($url));
	}

	# ���y�[�W�ԍ�
	if (($start + @users) < $usercount && $tmpl->query(name => 'FORWARDPAGELOOP') eq 'LOOP') {
		my $no = int($start / $size) + 1;
		my $maxno = int($usercount / $size);
		if ($usercount % $size) {
			$maxno++;
		}
		my @pagedata = ();
		for (my $i = $no + 1; $i <= $maxno; $i++) {
			my %page;
			my $url = $cgi->url(-relative=>1);
			$url .= '?start='.($i-1) * $size;
			$url .= '&size='.$size;
			$url .= &getCondUrl();
			if ($tmpl->query(name => ['FORWARDPAGELOOP', 'FORWARDPAGEURL']) eq 'VAR') {
				$page{FORWARDPAGEURL} = &convertOutput($url);
			}
			if ($tmpl->query(name => ['FORWARDPAGELOOP', 'FORWARDPAGELABEL']) eq 'VAR') {
				$page{FORWARDPAGELABEL} = $i;
			}
			push(@pagedata, \%page);
			# 9 �y�[�W�ȏ�͈ړ��ł��Ȃ�
			if (@pagedata >= 9) {
				last;
			}
		}
		$tmpl->param(FORWARDPAGELOOP => \@pagedata);
	}

	# ���݃y�[�W
	if ($tmpl->query(name => 'NOWPAGENOLABEL') eq 'VAR') {
		# �y�[�W��������ꍇ�����\��
		if ($size < $usercount) {
			my $no = int($start / $size) + 1;
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
	return $url;
}

######
# �W�v
sub addup {
	# �W�v�e�[�u���X�V
	my @allusers = &selectFetchArrayRef($dbh, 'SELECT userid FROM users WHERE deleteflag=?', '0');
	foreach my $row(@allusers) {
		my ($userid) = @$row;
		
		my $messagecount = &selectFetch($dbh, 'SELECT count(*) FROM messages WHERE sender_userid=?', $userid);
		my $topiccount = &selectFetch($dbh, 'SELECT count(*) FROM topics WHERE registuserid=? AND deleteflag=?', ($userid, '0'));
		my $topiccommentcount = &selectFetch($dbh, 'SELECT count(*) FROM topiccomments WHERE registuserid=? AND deleteflag=?', ($userid, '0'));

		if (&selectFetch($dbh, 'SELECT count(*) FROM addup WHERE userid=?', $userid)) {
			my $sql = 
				'UPDATE addup SET'.
				' messagecount=?,'.
				' topiccount=?,'.
				' topiccommentcount=?'.
				' WHERE'.
				' userid=?';
			my @bind = ($messagecount, $topiccount, $topiccommentcount, $userid);
			&doDB($dbh, $sql, @bind);
		} else {
			my $sql = 
				'INSERT addup ('.
				' userid,'.
				' messagecount,'.
				' topiccount,'.
				' topiccommentcount'.
				') VALUES (?, ?, ?, ?)';
			my @bind = ($userid, $messagecount, $topiccount, $topiccommentcount);
			&doDB($dbh, $sql, @bind);
		}
	}
}
	
##################
# �W�v���ʎ擾
sub getAddup {
	$usercount = 0;
	@users = ();

	$size = $cgi->param('size') + 0;
	if (!$size) {
		$size = 20;
	}

	# �����擾
	$usercount = &selectFetch($dbh, 'SELECT count(*) FROM addup a, users b WHERE a.userid=b.userid AND b.deleteflag=?', '0');

	# �f�[�^������
	if ($usercount) {
		if ($cgi->param('start')) {
			$start = $cgi->param('start') + 0;
		}

		my $sql =
			'SELECT'.
			' a.userid,'.
			' a.messagecount,'.
			' a.topiccount,'.
			' a.topiccommentcount,'.
			' b.name'.
			' FROM'.
			' addup a,'.
			' users b'.
			' WHERE'.
			' a.userid=b.userid'.
			' AND b.deleteflag=?'.
			' ORDER BY b.registtime';
		if ($usercount >= $size) {
			$sql .= ' LIMIT '.$start.', '.$size;
		}
		@users = &selectFetchArrayRef($dbh, $sql, '0');
		
	}
}

