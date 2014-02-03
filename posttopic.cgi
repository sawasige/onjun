#!/usr/bin/perl -w
use strict;
use CGI::Carp qw(fatalsToBrowser); # �G���[���b�Z�[�W��\������i���Ȃ��ꍇ�R�����g�A�E�g�j
use CGI;
use CGI::Session;
use HTML::Template;
require './config.pl';
require './global.pl';
require './vars.pl';
require './post.pl';
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

		# �o�^
		my $check = 0;
		if ($cgi->param('submit')) {
			$check = &checkTopic();
		}

		# ��ʕ\��
		if (!$check) {
			# ���݂̉��
			$msg .= &checkOnline($dbh, $session->param('userid'), '�V�K�g�s�b�N�쐬');

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

	# �t�H�[�������L��
	if ($forumname) {
		# ���[�����M�y�[�WURL
		if ($tmpl->query(name => ['MAILTOPICURL']) eq 'VAR') {
			my $url = 'mailtopic.cgi?forumid='.$forumid;
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(MAILTOPICURL => &convertOutput($url));
		}

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

		my $title = '';
		my $body = '';
		my $check = 1;
		if ($cgi->param('cancel')) {
			$title = $session->param('title');
			$body = $session->param('body');
			if (!$title) {
				$msg .= '�g�s�b�N�̏�񂪎����܂����B';
				$check = 0;
			}
		} elsif ($cgi->param('submit')) {
			$title = $cgi->param('title');
			$body = $cgi->param('body');
		}

		if ($check) {
			# �^�C�g��
			if ($tmpl->query(name => 'TOPICTITLE') eq 'VAR') {
				$tmpl->param(TOPICTITLE => &convertOutput($title));
			}
			# �{��
			if ($tmpl->query(name => 'BODY') eq 'VAR') {
				$tmpl->param(BODY => &convertOutput($body));
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

####################
# �t�H�[�������擾
sub getForumInfo() {
	# �t�H�[����ID
	if ($cgi->param('cancel')) {
		$forumid = $session->param('forumid');
	} else {
		$forumid = $cgi->param('forumid');
	}
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

###############
# ���̓`�F�b�N
sub checkTopic() {
	if ($msg) {
		return 0;
	}

	my %data;
	$data{'title'} = $cgi->param('title');
	$data{'body'} = $cgi->param('body');
	$data{'file1'} = $cgi->param('file1');
	$data{'file2'} = $cgi->param('file2');
	$data{'file3'} = $cgi->param('file3');
	$msg .= &postData($dbh, $forumid, 'tp', \%data, $sid);
	if ($msg) {
		return 0;
	}

	# ���̓`�F�b�N�����I�I
	$session->param('forumid', $forumid);
	$session->param('title', $data{'title'});
	$session->param('body', $data{'body'});
	$session->param('fname1', $data{'fname1'});
	$session->param('lname1', $data{'lname1'});
	$session->param('sname1', $data{'sname1'});
	$session->param('fname2', $data{'fname2'});
	$session->param('lname2', $data{'lname2'});
	$session->param('sname2', $data{'sname2'});
	$session->param('fname3', $data{'fname3'});
	$session->param('lname3', $data{'lname3'});
	$session->param('sname3', $data{'sname3'});
	$session->flush();

	# ��ʃ��_�C���N�g
	if (&isMobile()) {
		# �Z�b�V������ URL ���ߍ���
		print $cgi->redirect('posttopicconfirm.cgi?'.$config{'sessionname'}.'='.$sid);
	} else {
		# �Z�b�V������ Cookie ���ߍ���
		print $cgi->redirect('posttopicconfirm.cgi');
	}

	return 1;
}

