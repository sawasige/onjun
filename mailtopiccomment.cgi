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

		# �g�s�b�N���擾
		&getTopicInfo();

		# ���݂̉��
		$msg .= &checkOnline($dbh, $session->param('userid'), '�g�s�b�N�R�����g���[�����e');

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

	# �g�s�b�N���L��
	if ($topictitle) {
		# ���[�����M�y�[�WURL
		if ($tmpl->query(name => ['MAILTOPICCOMMENTURL']) eq 'VAR') {
			my $url = 'mailtopiccomment.cgi?topicid='.$topicid;
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(MAILTOPICCOMMENTURL => &convertOutput($url));
		}

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

		if ($tmpl->query(name => ['MAILTOTOPICCOMMENT']) eq 'VAR' || 
			$tmpl->query(name => ['URL_RECEIVEMAIL']) eq 'VAR') {

			# ���[���L�[
			my $mailkey = &getMailKey();

			# ���[�����MURL
			if ($tmpl->query(name => ['MAILTOTOPICCOMMENT']) eq 'VAR') {
				my $subject = $mailkey;
				my $url = 'mailto:'.$config{'postmail'}.'?subject='.$subject;
				$tmpl->param(MAILTOTOPICCOMMENT => &convertOutput($url));
			}

			# ���[�����e�m�F�� URL
			if ($tmpl->query(name => 'URL_RECEIVEMAIL') eq 'VAR') {
				my $url = 'receivemail.cgi?mailkey='.$mailkey;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
				$tmpl->param(URL_RECEIVEMAIL => &convertOutput($url));
			}
			
		}

		# �R�����g������ URL
		if ($tmpl->query(name => ['URL_POSTTOPICCOMMENT']) eq 'VAR') {
			my $url = 'posttopiccomment.cgi?topicid='.$topicid;
			if (&isMobile) {
				$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(URL_POSTTOPICCOMMENT => &convertOutput($url));
		}
	}
	
	# ���b�Z�[�W�i����΁j
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

####################
# �g�s�b�N���擾
sub getTopicInfo() {
	# �g�s�b�NID
	$topicid = $cgi->param('topicid');
	
	my $sql = 
		'SELECT a.forumid, a.name, a.note, b.title, b.body'.
		' FROM forums a, topics b'.
		' WHERE a.forumid=b.forumid AND b.topicid=? AND a.deleteflag=? AND b.deleteflag=? AND a.powerlevel<=?';
	my @bind = ($topicid, '0', '0', $session->param('powerlevel'));
	my ($fid, $fname, $fnote, $ttitle, $tbody) = &selectFetchArray($dbh, $sql, @bind);
	$forumid = $fid;
	$forumname = $fname;
	$forumnote = $fnote;
	$topictitle = $ttitle;
	$topicbody = $tbody;
	if (!$forumname) {
		$msg .= '�p�����[�^���s���ł��B';
	}
}


##############################
# ���[�����e�̃T�u�W�F�N�g����
sub getMailKey() {

	# �d���`�F�b�N
	my @bind = ('0', 'tc', $topicid, $session->param('userid'));
	my ($mailkeyid, $keystr) = &selectFetchArray($dbh, 'SELECT mailkeyid, keystr FROM mailkeys WHERE deleteflag=? AND kind=? AND id=? AND registuserid=?', @bind);
	if (!$mailkeyid) {
		$keystr = &getRandomString(5);
		my $sql = 
			'INSERT INTO mailkeys('.
			' kind,'.
			' id,'.
			' keystr,'.
			' registuserid,'.
			' registtime'.
			') VALUES (?, ?, ?, ?, now())';
		&doDB($dbh, $sql, ('tc', $topicid, $keystr, $session->param('userid')));
		$mailkeyid = &selectFetch($dbh, 'SELECT LAST_INSERT_ID()');
	}
	return 'post'.$mailkeyid.'_'.$keystr;
}

