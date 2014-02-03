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
my $messagecount = 0;
my @messages = ();

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

		# �ꗗ�擾
		&getList();

		# ���݂̉��
		$msg .= &checkOnline($dbh, $session->param('userid'), '���M�ς݃��b�Z�[�W�ꗗ');

		# ��ʕ\��
		&disp();

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

	# ���b�Z�[�W
	$msg .= $session->param('msg');
	$session->clear(['msg']);
	$session->flush();
	
	# ���b�Z�[�W�ꗗ
	if (@messages && $tmpl->query(name => 'MESSAGES') eq 'LOOP') {
		my @messagedata = ();
		foreach my $row(@messages) {
			my ($messageid, $subject, $receiverid, $receivername, $time) = @$row;
			my %message;
			if ($tmpl->query(name => ['MESSAGES', 'URL']) eq 'VAR') {
				my $url = 'sendmessageview.cgi?messageid='.$messageid;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$message{'URL'} = &convertOutput($url);
			}
			if ($tmpl->query(name => ['MESSAGES', 'SUBJECT']) eq 'VAR') {
				$message{'SUBJECT'} = &convertOutput($subject);
			}
			if ($tmpl->query(name => ['MESSAGES', 'RECEIVER']) eq 'VAR') {
				$message{'RECEIVER'} = &convertOutput($receivername);
			}
			if ($tmpl->query(name => ['MESSAGES', 'RECEIVERURL']) eq 'VAR') {
				my $url = 'profile.cgi?userid='.$receiverid;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$message{'RECEIVERURL'} = &convertOutput($url);
			}
			if ($tmpl->query(name => ['MESSAGES', 'TIME']) eq 'VAR') {
				$message{'TIME'} = &convertOutput($time);
			}
			push(@messagedata, \%message);
		}
		$tmpl->param(MESSAGES => \@messagedata);
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
	if (($cgi->param('start') + @messages) < $messagecount && $tmpl->query(name => 'NEXTPAGEURL') eq 'VAR') {
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
	if (($cgi->param('start') + @messages) < $messagecount && $tmpl->query(name => 'FORWARDPAGELOOP') eq 'LOOP') {
		my $pagesize = $cgi->param('size') + 0;
		if (!$pagesize) {
			$pagesize = 10;
		}
		my $start = $cgi->param('start') + 0;
		my $no = int($start / $pagesize) + 1;
		my $maxno = int($messagecount / $pagesize);
		if ($messagecount % $pagesize) {
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
		if ($pagesize < $messagecount) {
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
	return $url;
}

###########
# �ꗗ�擾
sub getList() {
	if ($msg) {
		return 0;
	}

	# �������s
	my $pagesize = $cgi->param('size') + 0;
	if (!$pagesize) {
		$pagesize = 10; # �f�t�H���g�T�C�Y
	}
	my $pagestart = $cgi->param('start') + 0;
	my @bind = ($session->param('userid'), '0');
	my $sqlcount = 'SELECT count(*) FROM messages a, users b';
	my $sql = 'SELECT a.messageid, a.subject, b.userid, b.name, a.sendtime FROM messages a, users b';
	my $sqlwhere = ' WHERE a.receiver_userid=b.userid AND a.sender_userid=? AND a.sender_deleteflag=? ';
	$sqlcount .= $sqlwhere;
	$sql .= $sqlwhere.' ORDER BY sendtime DESC';

	@messages = ();
	$messagecount = &selectFetch($dbh, $sqlcount, @bind);
	if ($messagecount >= $pagesize) {
		$sql .= ' LIMIT '.$pagestart.', '.$pagesize;
	}
	@messages = &selectFetchArrayRef($dbh, $sql, @bind);

	return 1;
}
