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
my $newscount = 0;
my @news = ();
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
		$sid = $session->id;

		# DB �I�[�v��
		$dbh = &connectDB(1);

		# �V���ꗗ�擾
		&getNewsList();

		# ���݂̉��
		$msg .= &checkOnline($dbh, $session->param('userid'), '�t�H�[�����̍ŐV�̏�������');

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

	# ���b�Z�[�W
	$msg .= $session->param('msg');
	$session->clear(['msg']);
	$session->flush();
	
	# �V���ꗗ
	if (@news && $tmpl->query(name => 'MORENEWS') eq 'LOOP') {
		my @newsvars = ();
		foreach my $row(@news) {
			my ($forumid, $forumname, $topicid, $title, $lastcommentid, $lastuserid, $lastusername, $lasttime, $commentcount) = @$row;
			my %newsvar = ();
			# ����
			if ($tmpl->query(name => ['MORENEWS', 'TIME']) eq 'VAR') {
				$newsvar{'TIME'} = &convertOutput($lasttime);
			}
			# ���t
			if ($tmpl->query(name => ['MORENEWS', 'DATE']) eq 'VAR') {
				if ($lasttime =~ /^(\d{4})\-(\d{2})\-(\d{2}) /) {
					$newsvar{'DATE'} = &convertOutput($2.'��'.$3.'��');
				}
			}
			# �g�s�b�N�^�C�g��
			if ($tmpl->query(name => ['MORENEWS', 'TOPICTITLE']) eq 'VAR') {
				$newsvar{'TOPICTITLE'} = &convertOutput($title);
			}
			# �g�s�b�NURL
			if ($tmpl->query(name => ['MORENEWS', 'URL']) eq 'VAR') {
				my $url = 'topic.cgi?';
				if ($lastcommentid) {
					$url .= 'topiccommentid='.$lastcommentid;
				} else {
					$url .= 'topicid='.$topicid;
				}
				if (&isMobile()) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id();
				}
				if ($lastcommentid) {
					$url .= '#'.$lastcommentid;
				}
				$newsvar{'URL'} = &convertOutput($url);
			}
			# �g�s�b�N�R�����g��
			if ($tmpl->query(name => ['MORENEWS', 'COUNT']) eq 'VAR') {
				$newsvar{'COUNT'} = &convertOutput($commentcount);
			}
			# �t�H�[������
			if ($tmpl->query(name => ['MORENEWS', 'FORUMNAME']) eq 'VAR') {
				$newsvar{'FORUMNAME'} = &convertOutput($forumname);
			}
			# �t�H�[����URL
			if ($tmpl->query(name => ['MORENEWS', 'FORUMURL']) eq 'VAR') {
				my $url = 'forum.cgi?topicid='.$topicid;
				if (&isMobile()) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id();
				}
				$url .= '#'.$topicid;
				$newsvar{'FORUMURL'} = &convertOutput($url);
			}
			# �ŏI���e��
			if ($tmpl->query(name => ['MORENEWS', 'LASTUSERNAME']) eq 'VAR') {
				$newsvar{'LASTUSERNAME'} = &convertOutput($lastusername);
			}
			# �ŏI���e��URL
			if ($tmpl->query(name => ['MORENEWS', 'LASTUSERURL']) eq 'VAR') {
				my $url = 'profile.cgi?userid='.$lastuserid;
				if (&isMobile()) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id();
				}
				$newsvar{'LASTUSERURL'} = &convertOutput($url);
			}
			push(@newsvars, \%newsvar);
		}
		$tmpl->param(MORENEWS=> \@newsvars);
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
	if (($start + @news) < $newscount && $tmpl->query(name => 'NEXTPAGEURL') eq 'VAR') {
		my $nextstart = $start + $size;
		my $url = $cgi->url(-relative=>1);
		$url .= '?start='.$nextstart;
		$url .= '&size='.$size;
		$url .= &getCondUrl();
		$tmpl->param(NEXTPAGEURL => &convertOutput($url));
	}

	# ���y�[�W�ԍ�
	if (($start + @news) < $newscount && $tmpl->query(name => 'FORWARDPAGELOOP') eq 'LOOP') {
		my $no = int($start / $size) + 1;
		my $maxno = int($newscount / $size);
		if ($newscount % $size) {
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
		if ($size < $newscount) {
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
	if (&isMobile()) {
		$url .= '&'.$config{'sessionname'}.'='.$session->id();
	}
	return $url;
}


#####################
# �V���ꗗ�擾
sub getNewsList() {
	$newscount = 0;
	@news = ();

	$size = $cgi->param('size') + 0;
	if (!$size) {
		$size = 10;
	}

	# �����擾
	my $sql = 
			'SELECT'.
			' count(*)'.
			' FROM'.
			' topics a,'.
			' users c,'.
			' forums d'.
			' WHERE'.
			' a.lastuserid=c.userid AND'.
			' a.forumid=d.forumid AND'.
			' a.deleteflag=? AND'.
			' d.deleteflag=? AND'.
			' d.powerlevel<=?';
	my @bind = ('0', '0', $session->param('powerlevel'));
	$newscount = &selectFetch($dbh, $sql, @bind);

	# �f�[�^������
	if ($newscount) {
		if ($cgi->param('start')) {
			$start = $cgi->param('start') + 0;
		}

		my $sql = 
			'SELECT'.
			' a.forumid,'.
			' d.name,'.
			' a.topicid,'.
			' a.title,'.
			' a.lastcommentid,'.
			' a.lastuserid,'.
			' c.name,'.
			' a.lasttime,'.
			' a.commentcount'.
			' FROM'.
			' topics a,'.
			' users c,'.
			' forums d'.
			' WHERE'.
			' a.lastuserid=c.userid AND'.
			' a.forumid=d.forumid AND'.
			' a.deleteflag=? AND'.
			' d.deleteflag=? AND'.
			' d.powerlevel<=?'.
			' ORDER BY a.lasttime DESC';
		if ($newscount >= $size) {
			$sql .= ' LIMIT '.$start.', '.$size;
		}
		my @bind = ('0', '0', $session->param('powerlevel'));
		@news = &selectFetchArrayRef($dbh, $sql, @bind);
	}
}
