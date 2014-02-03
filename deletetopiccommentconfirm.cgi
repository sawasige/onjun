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
				print $cgi->redirect("topic.cgi?topicid=$topicid&$config{'sessionname'}=$sid");
			} else {
				# �Z�b�V������ Cookie ���ߍ��܂�Ă���
				print $cgi->redirect("topic.cgi?topicid=$topicid");
			}
		} else {
			# DB �I�[�v��
			$dbh = &connectDB(1);

			# �g�s�b�N�R�����g���擾
			&getTopicCommentInfo();
			

			# �o�^
			my $check = 0;
			if ($cgi->param('submit')) {
				$check = &deleteTopicComment();
			}

			# ��ʕ\��
			if (!$check) {
				# ���݂̉��
				$msg .= &checkOnline($dbh, $session->param('userid'), '�g�s�b�N�R�����g�폜�m�F');

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
		my $title = $session->param('title');
		my $body = $session->param('body');

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

##########################
# �g�s�b�N�R�����g���擾
sub getTopicCommentInfo() {
	# �g�s�b�NID
	$topiccommentid = $cgi->param('topiccommentid');
	
	my $sql = 
		'SELECT a.forumid, a.name, a.note, b.topicid, b.title, b.body, c.body'.
		' FROM forums a, topics b, topiccomments c'.
		' WHERE a.forumid=b.forumid AND b.topicid=c.topicid AND c.topiccommentid=? AND a.deleteflag=? AND b.deleteflag=? AND c.deleteflag=? AND a.powerlevel<=?';
	my @bind = ($topiccommentid, '0', '0', '0', $session->param('powerlevel'));
	# �Ǘ��҈ȊO�͏������񂾓��l�̂�
	if ($session->param('powerlevel') < 5) {
		$sql .= ' AND c.registuserid=?';
		push(@bind, $session->param('userid'));
	}
	my ($fid, $fname, $fnote, $tid, $ttitle, $tbody, $cbody) = &selectFetchArray($dbh, $sql, @bind);
	$forumid = $fid;
	$forumname = $fname;
	$forumnote = $fnote;
	$topicid = $tid;
	$topictitle = $ttitle;
	$topicbody = $tbody;
	$topiccommentbody = $cbody;
	if (!$topiccommentbody) {
		$msg .= '�p�����[�^���s���ł��B';
	}
}

###############
# �g�s�b�N�C��
sub deleteTopicComment() {
	if ($msg) {
		return 0;
	}

	my $userid = $session->param('userid');
	
	# �Ǘ��҈ȊO�͏������񂾓��l�̂�
	if ($session->param('powerlevel') < 5) {
		my @bind = ($topiccommentid, $userid, '0');
		my $count = &selectFetch($dbh, 'SELECT count(*) FROM topiccomments WHERE topiccommentid=? AND registuserid=? AND deleteflag=?', @bind);
		if (!$count) {
			$msg .= '�p�����[�^���s���ł��B';
			return 0;
		}
	} else {
		$userid = &selectFetch($dbh, 'SELECT registuserid FROM topiccomments WHERE topiccommentid=? AND deleteflag=?', ($topiccommentid, '0'));
	}

	# DB �o�^
	my @bind = ('1', $topiccommentid);
	my $sql = 'UPDATE topiccomments SET deleteflag=? WHERE topiccommentid=?';
	&doDB($dbh, $sql, @bind);

	my $lastcommentid = &selectFetch($dbh, 'SELECT max(topiccommentid) FROM topiccomments WHERE deleteflag=? AND topicid=?', ('0', $topicid));
	if ($lastcommentid) {
		my $commentcount = &selectFetch($dbh, 'SELECT count(*) FROM topiccomments WHERE deleteflag=? AND topicid=?', ('0', $topicid));
		my ($lastuserid, $lasttime) = &selectFetchArray($dbh, 'SELECT registuserid, registtime FROM topiccomments WHERE topiccommentid=?', ($lastcommentid));
		&doDB($dbh, 'UPDATE topics SET lastcommentid=?, lastuserid=?, lasttime=?, commentcount=? WHERE topicid=?', ($lastcommentid, $lastuserid, $lasttime, $commentcount, $topicid));
	} else {
		my ($lastuserid, $lasttime) = &selectFetchArray($dbh, 'SELECT registuserid, registtime FROM topics WHERE topicid=?', ($topicid));
		&doDB($dbh, 'UPDATE topics SET lastcommentid=?, lastuserid=?, lasttime=? , commentcount=? WHERE topicid=?', (0, $lastuserid, $lasttime, 0, $topicid));
	}

	# �t�@�C���폜
	&hideFile('tc'.$topiccommentid);

	$msg .= '�R�����g���폜���܂����B';
	$session->param('msg', $msg);
	$session->flush();

	# �W�v
	if (&selectFetch($dbh, 'SELECT count(*) FROM addup WHERE userid=?', $userid)) {
		my $sql = 
			'UPDATE addup SET'.
			' topiccommentcount=topiccommentcount-1'.
			' WHERE'.
			' userid=?';
		my @bind = ($userid);
		&doDB($dbh, $sql, @bind);
	}

	# ��ʃ��_�C���N�g
	if (&isMobile()) {
		# �Z�b�V������ URL ���ߍ���
		print $cgi->redirect("topic.cgi?topicid=$topicid&$config{'sessionname'}=$sid");
	} else {
		# �Z�b�V������ Cookie ���ߍ��܂�Ă���
		print $cgi->redirect('topic.cgi?topicid='.$topicid);
	}

	return 1;
}

