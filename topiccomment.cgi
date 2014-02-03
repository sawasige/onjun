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
my $forumid = 0;
my $forumname = '';
my $forumnote = '';
my $topicid = 0;
my $topictitle = '';
my $topicbody = '';
my $topiccommentid = 0;
my $topiccommentbody = '';
my $topiccommentregistuserid = 0;
my $topiccommentregisttime = '';
my $topiccommentregistusername = '';

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

		# �g�s�b�N�R�����g���擾
		&getTopicCommentInfo();

		# ���݂̉��
		$msg .= &checkOnline($dbh, $session->param('userid'), '�g�s�b�N�R�����g');

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
	


	# �g�s�b�N�R�����g���L��
	if ($topiccommentbody) {
		# �t�H�[����ID
		if ($tmpl->query(name => ['FORUMID']) eq 'VAR') {
			$tmpl->param(FORUMID => $forumid);
		}
		# �t�H�[����URL
		if ($tmpl->query(name => ['FORUMURL']) eq 'VAR') {
			my $url = 'forum.cgi?forumid='.$forumid;
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(FORUMURL => &convertOutput($url));
		}
		# �t�H�[������
		if ($tmpl->query(name => ['FORUMNAME']) eq 'VAR') {
			$tmpl->param(FORUMNAME => &convertOutput($forumname));
		}
		# �t�H�[��������
		if ($tmpl->query(name => ['FORUMNOTE']) eq 'VAR') {
			$tmpl->param(FORUMNOTE => &convertOutput($forumnote, 1));
		}
		# �g�s�b�NID
		if ($tmpl->query(name => ['TOPICID']) eq 'VAR') {
			$tmpl->param(TOPICID => $topicid);
		}
		# �g�s�b�NURL
		if ($tmpl->query(name => ['TOPICURL']) eq 'VAR') {
			my $url = 'topic.cgi?topicid='.$topicid;
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(TOPICURL => &convertOutput($url));
		}
		# �g�s�b�N�^�C�g��
		if ($tmpl->query(name => ['TOPICTITLE']) eq 'VAR') {
			$tmpl->param(TOPICTITLE => &convertOutput($topictitle));
		}
		# �g�s�b�N�{��
		if ($tmpl->query(name => ['TOPICBODY']) eq 'VAR') {
			$tmpl->param(TOPICBODY => &convertOutput($topicbody, 1));
		}
		# �g�s�b�N�R�����gID
		if ($tmpl->query(name => ['TOPICCOMMENTID']) eq 'VAR') {
			$tmpl->param(TOPICCOMMENTID => &convertOutput($topiccommentid));
		}
		# �g�s�b�N�R�����g
		if ($tmpl->query(name => ['TOPICCOMMENTBODY']) eq 'VAR') {
			$tmpl->param(TOPICCOMMENTBODY => &convertOutput($topiccommentbody, 1));
		}

		# �o�^����
		if ($topiccommentregisttime && $tmpl->query(name => ['TOPICCOMMENTREGISTTIME']) eq 'VAR') {
			$tmpl->param(TOPICCOMMENTREGISTTIME => $topiccommentregisttime);
		}
		
		# �o�^��
		if ($topiccommentregistusername && $tmpl->query(name => ['TOPICCOMMENTREGISTUSERNAME']) eq 'VAR') {
			$tmpl->param(TOPICCOMMENTREGISTUSERNAME => &convertOutput($topiccommentregistusername));
		}
		
		# �o�^��URL
		if ($topiccommentregistuserid && $tmpl->query(name => ['TOPICCOMMENTREGISTUSERURL']) eq 'VAR') {
			my $url = 'profile.cgi?userid='.$topiccommentregistuserid;
			if (&isMobile) {
				$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(TOPICCOMMENTREGISTUSERURL => &convertOutput($url));
		}

		# �g�s�b�N�R�����g�C��URL
		if (($session->param('userid') eq $topiccommentregistuserid || $session->param('powerlevel') >= 5) && $tmpl->query(name => ['MODIFYTOPICCOMMENTURL']) eq 'VAR') {
			my $url = 'modifytopiccomment.cgi?topiccommentid='.$topiccommentid;
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(MODIFYTOPICCOMMENTURL => &convertOutput($url));
		}
		# �g�s�b�N�R�����g�폜URL
		if (($session->param('userid') eq $topiccommentregistuserid || $session->param('powerlevel') >= 5) && $tmpl->query(name => ['DELETETOPICCOMMENTURL']) eq 'VAR') {
			my $url = 'deletetopiccommentconfirm.cgi?topiccommentid='.$topiccommentid;
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(DELETETOPICCOMMENTURL => &convertOutput($url));
		}

		# �R�����g������URL
		if ($tmpl->query(name => ['POSTTOPICCOMMENTURL']) eq 'VAR') {
			my $url = 'posttopiccomment.cgi?topicid='.$topicid;
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(POSTTOPICCOMMENTURL => &convertOutput($url));
		}

		# �V�K�g�s�b�N�쐬URL
		if ($tmpl->query(name => ['URL_POSTTOPIC']) eq 'VAR') {
			my $url = 'posttopic.cgi?forumid='.$forumid;
			if (&isMobile) {
				$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(URL_POSTTOPIC => &convertOutput($url));
		}
	}

	# �Y�t�t�@�C��1
	if ($tmpl->query(name => ['FILE1LARGEURL']) eq 'VAR') {
		my $lname1 = &getPublishFile('tc'.$topiccommentid.'_1');
		if ($lname1) {
			$tmpl->param(FILE1LARGEURL => $lname1);
			if ($tmpl->query(name => ['FILE1SMALLURL']) eq 'VAR') {
				my $sname1 = &getPublishFile('tc'.$topiccommentid.'_1_s');
				if ($sname1) {
					$tmpl->param(FILE1SMALLURL => $sname1);
				}
			}
		}
	}

	# �Y�t�t�@�C��2
	if ($tmpl->query(name => ['FILE2LARGEURL']) eq 'VAR') {
		my $lname2 = &getPublishFile('tc'.$topiccommentid.'_2');
		if ($lname2) {
			$tmpl->param(FILE2LARGEURL => $lname2);
			if ($tmpl->query(name => ['FILE2SMALLURL']) eq 'VAR') {
				my $sname2 = &getPublishFile('tc'.$topiccommentid.'_2_s');
				if ($sname2) {
					$tmpl->param(FILE2SMALLURL => $sname2);
				}
			}
		}
	}

	# �Y�t�t�@�C��3
	if ($tmpl->query(name => ['FILE3LARGEURL']) eq 'VAR') {
		my $lname3 = &getPublishFile('tc'.$topiccommentid.'_3');
		if ($lname3) {
			$tmpl->param(FILE3LARGEURL => $lname3);
			if ($tmpl->query(name => ['FILE3SMALLURL']) eq 'VAR') {
				my $sname3 = &getPublishFile('tc'.$topiccommentid.'_3_s');
				if ($sname3) {
					$tmpl->param(FILE3SMALLURL => $sname3);
				}
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

##########################
# �g�s�b�N�R�����g���擾
sub getTopicCommentInfo() {
	# �g�s�b�N�R�����gID
	$topiccommentid = $cgi->param('topiccommentid');
	my $sql = 
		'SELECT a.forumid,'.
		' a.name,'.
		' a.note,'.
		' b.topicid,'.
		' b.title,'.
		' b.body,'.
		' c.body,'.
		' c.registuserid,'.
		' c.registtime,'.
		' d.name'.
		' FROM'.
		' forums a,'.
		' topics b,'.
		' topiccomments c,'.
		' users d'.
		' WHERE'.
		' a.forumid=b.forumid'.
		' AND b.topicid=c.topicid'.
		' AND c.registuserid=d.userid'.
		' AND c.topiccommentid=?'.
		' AND a.deleteflag=?'.
		' AND b.deleteflag=?'.
		' AND c.deleteflag=?'.
		' AND a.powerlevel<=?';
	my @bind = ($topiccommentid, '0', '0', '0', $session->param('powerlevel'));
	my ($fid, $fname, $fnote, $tid, $ttitle, $tbody, $cbody, $cuserid, $ctime, $uname) = &selectFetchArray($dbh, $sql, @bind);
	$forumid = $fid;
	$forumname = $fname;
	$forumnote = $fnote;
	$topicid = $tid;
	$topictitle = $ttitle;
	$topicbody = $tbody;
	$topiccommentbody = $cbody;
	$topiccommentregistuserid = $cuserid;
	$topiccommentregisttime = $ctime;
	$topiccommentregistusername = $uname;
	if (!$topiccommentbody) {
		$msg .= '�p�����[�^���s���ł��B';
	}
}

