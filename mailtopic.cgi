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

		# �t�H�[�������擾
		&getForumInfo();

		# ���݂̉��
		$msg .= &checkOnline($dbh, $session->param('userid'), '�g�s�b�N���[�����e');

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

	# �t�H�[�������L��
	if ($forumname) {
		# �t�H�[����ID
		if ($forumname && $tmpl->query(name => ['FORUMID']) eq 'VAR') {
			$tmpl->param(FORUMID => &convertOutput($forumid));
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
		if ($forumname && $tmpl->query(name => ['FORUMNAME']) eq 'VAR') {
			$tmpl->param(FORUMNAME => &convertOutput($forumname));
		}
		# �t�H�[��������
		if ($forumnote && $tmpl->query(name => ['FORUMNOTE']) eq 'VAR') {
			$tmpl->param(FORUMNOTE => &convertOutput($forumnote, 1));
		}

		if ($tmpl->query(name => ['MAILTOTOPIC']) eq 'VAR' || 
			$tmpl->query(name => ['URL_RECEIVEMAIL']) eq 'VAR') {

			# ���[���L�[
			my $mailkey = &getMailKey();

			# ���[�����MURL
			if ($tmpl->query(name => ['MAILTOTOPIC']) eq 'VAR') {
				my $subject = $mailkey;
				my $url = 'mailto:'.$config{'postmail'}.'?subject='.$subject;
				$tmpl->param(MAILTOTOPIC => &convertOutput($url));
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
		
		# �V�K�g�s�b�NURL
		if ($tmpl->query(name => ['URL_POSTTOPIC']) eq 'VAR') {
			my $url = 'posttopic.cgi?forumid='.$forumid;
			if (&isMobile) {
				$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(URL_POSTTOPIC => &convertOutput($url));
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
# �t�H�[�������擾
sub getForumInfo() {
	$forumid = $cgi->param('forumid');
	my $sql = 
		'SELECT name, note'.
		' FROM forums'.
		' WHERE forumid=? AND deleteflag=? AND powerlevel<=?';
	my @bind = ($forumid, '0', $session->param('powerlevel'));
	my ($name, $note) = &selectFetchArray($dbh, $sql, @bind);
	$forumname = $name;
	$forumnote = $note;
	if (!$name) {
		$msg .= '�p�����[�^���s���ł��B';
	}
}

##############################
# ���[�����e�̃T�u�W�F�N�g����
sub getMailKey() {

	# �d���`�F�b�N
	my @bind = ('0', 'tp', $forumid, $session->param('userid'));
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
		&doDB($dbh, $sql, ('tp', $forumid, $keystr, $session->param('userid')));
		$mailkeyid = &selectFetch($dbh, 'SELECT LAST_INSERT_ID()');
	}
	return 'post'.$mailkeyid.'_'.$keystr;
}

