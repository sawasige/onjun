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
		
		# �L�����Z���Ȃ�߂�
		if ($cgi->param('cancel')) {
			# ��ʃ��_�C���N�g
			if (&isMobile()) {
				# �Z�b�V������ URL ���ߍ���
				print $cgi->redirect("posttopiccomment.cgi?cancel=1&$config{'sessionname'}=$sid");
			} else {
				# �Z�b�V������ Cookie ���ߍ��܂�Ă���
				print $cgi->redirect("posttopiccomment.cgi?cancel=1");
			}
		} else {
			# DB �I�[�v��
			$dbh = &connectDB(1);

			# �g�s�b�N���擾
			&getTopicInfo();

			# �o�^
			my $check = 0;
			if ($cgi->param('submit')) {
				$check = &writeComment();
			}

			# ��ʕ\��
			if (!$check) {
				# ���݂̉��
				$msg .= &checkOnline($dbh, $session->param('userid'), '�g�s�b�N�R�����g���e�m�F');

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

	if (!$msg) {
		my $body = $session->param('body');
		my $fname1 = $session->param('fname1');
		my $fname2 = $session->param('fname2');
		my $fname3 = $session->param('fname3');

		# �g�s�b�N���L��
		if ($topictitle) {
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

			# �R�����g
			if ($tmpl->query(name => 'BODY') eq 'VAR') {
				$tmpl->param(BODY => &convertOutput($body, 1));
			}

			# �ʐ^1
			if ($tmpl->query(name => 'FILE1') eq 'VAR') {
				$tmpl->param(FILE1 => &convertOutput($fname1));
			}

			# �ʐ^2
			if ($tmpl->query(name => 'FILE2') eq 'VAR') {
				$tmpl->param(FILE2 => &convertOutput($fname2));
			}

			# �ʐ^3
			if ($tmpl->query(name => 'FILE3') eq 'VAR') {
				$tmpl->param(FILE3 => &convertOutput($fname3));
			}

		} else {
			$msg .= '�g�s�b�N�̏�񂪎����܂����B';
		}
	}
	
	# ���b�Z�[�W�i����΁j
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => &convertOutput($msg));
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

####################
# �g�s�b�N���擾
sub getTopicInfo() {
	# �g�s�b�NID
	$topicid = $session->param('topicid');
	
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

###################
# �R�����g��������
sub writeComment() {
	if ($msg) {
		return 0;
	}

	my %data;
	$data{'body'} = $session->param('body');
	$data{'fname1'} = $session->param('fname1');
	$data{'lname1'} = $session->param('lname1');
	$data{'sname1'} = $session->param('sname1');
	$data{'fname2'} = $session->param('fname2');
	$data{'lname2'} = $session->param('lname2');
	$data{'sname2'} = $session->param('sname2');
	$data{'fname3'} = $session->param('fname3');
	$data{'lname3'} = $session->param('lname3');
	$data{'sname3'} = $session->param('sname3');

	$msg .= &submitTopicComment($dbh, $topicid, \%data, $session->param('userid'));
	if ($msg) {
		return 0;
	}

	$msg .= '�R�����g���������݂܂����B';
	$session->clear(['topicid', 'body']);
	$session->param('msg', $msg);
	$session->flush();

	# ��ʃ��_�C���N�g
	if (&isMobile()) {
		# �Z�b�V������ URL ���ߍ���
		print $cgi->redirect("topic.cgi?topiccommentid=$data{'newtopiccommentid'}&$config{'sessionname'}=$sid#$data{'newtopiccommentid'}");
	} else {
		# �Z�b�V������ Cookie ���ߍ��܂�Ă���
		print $cgi->redirect('topic.cgi?topiccommentid='.$data{'newtopiccommentid'}.'#'.$data{'newtopiccommentid'});
	}

	return 1;
}

