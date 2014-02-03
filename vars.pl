use strict;
use CGI::Carp qw(fatalsToBrowser); # �G���[���b�Z�[�W��\������i���Ȃ��ꍇ�R�����g�A�E�g�j
use CGI;

require './global.pl';
require './jcode.pl';

# �ݒ�ǂݍ���
my %config = &getConfig;


###########################
# �Z�b�V�����L�����̃e���v���[�g�ϐ����ߍ���
sub setCommonVars($) {
	my $tmpl = shift;
	my $session = shift;
	my $dbh = shift;

	my $cgi = &getCGI();
	my $phone = &getPhone();

	my $sidurl = undef;
	my $powerlevel = undef;
	if ($session) {
		$sidurl = $config{'sessionname'}.'='.$session->id;
		$powerlevel = $session->param('powerlevel');
	}
	if (!$powerlevel) {
		$powerlevel = 1;
	}

	my $isMobile = &isMobile();

	my $msg = '';

	# ���[�U�[��
	if ($tmpl->query(name => 'USER') eq 'VAR') {
		my $user = $cgi->param('user') || $cgi->cookie('user') or '';
		$tmpl->param(USER => &convertOutput($user));
	}
	# �p�X���[�h
	if ($tmpl->query(name => 'PASS') eq 'VAR') {
		my $pass = $cgi->param('pass') || '';
		$tmpl->param(PASS => &convertOutput($pass));
	}

	# ���O�C���C���t�H���[�V����
	if ($session && $tmpl->query(name => 'INFO') eq 'VAR') {
		my $info = $session->param('info');
		$session->clear(['info']);
		$session->flush();
		if ($info) {
			$tmpl->param(INFO => $info);
		}
	}


	# �^�C�g��
	if ($tmpl->query(name => 'TITLE') eq 'VAR') {
		$tmpl->param(TITLE => $config{'title'});
	}
	
	# �T�u�^�C�g��
	if ($tmpl->query(name => 'SUBTITLE') eq 'VAR') {
		$tmpl->param(SUBTITLE => $config{'subtitle'});
	}
	
	# onjun ���m�点���[���A�h���X
	if ($tmpl->query(name => 'ADMINMAIL') eq 'VAR') {
		$tmpl->param(ADMINMAIL => $config{'adminmail'});
	}
	
	# ������ URL
	if ($tmpl->query(name => 'URL') eq 'VAR') {
		$tmpl->param(URL => $cgi->url(-relative=>1));
	}
	
	# �g�ђ[��
	if ($isMobile && $tmpl->query(name => 'MOBILE') eq 'VAR') {
		$tmpl->param(MOBILE => 1);
	}
	
	# �h�R���[��
	if ($phone->{type} eq "docomo" && $tmpl->query(name => 'DOCOMO') eq 'VAR') {
		$tmpl->param(DOCOMO => 1);
	}

	# �Z�b�V������
	if ($isMobile && $session && $tmpl->query(name => 'SESSIONNAME') eq 'VAR') {
		$tmpl->param(SESSIONNAME => $config{'sessionname'});
	}
	# �Z�b�V���� ID
	if ($isMobile && $session && $tmpl->query(name => 'SESSIONID') eq 'VAR') {
		$tmpl->param(SESSIONID => $session->id);
	}

	# �g�b�v�y�[�W URL
	if ($tmpl->query(name => 'URL_INDEX') eq 'VAR') {
		my $url = 'index.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_INDEX => &convertOutput($url));
	}

	# ���[�U�[�o�^�� URL
	if ($tmpl->query(name => 'URL_REGUSER') eq 'VAR') {
		my $url = 'reguser.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_REGUSER => &convertOutput($url));
	}

	# ��M���b�Z�[�W���X�g�� URL
	if ($tmpl->query(name => 'URL_RECEIVEMESSAGELIST') eq 'VAR') {
		my $url = 'receivemessagelist.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_RECEIVEMESSAGELIST => &convertOutput($url));
	}

	# ���M���b�Z�[�W���X�g�� URL
	if ($tmpl->query(name => 'URL_SENDMESSAGELIST') eq 'VAR') {
		my $url = 'sendmessagelist.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_SENDMESSAGELIST => &convertOutput($url));
	}

	# �t�H�[������ URL
	if ($tmpl->query(name => 'URL_FORUMLIST') eq 'VAR') {
		my $url = 'forumlist.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_FORUMLIST => &convertOutput($url));
	}

	# ���L�������� URL
	if ($tmpl->query(name => 'URL_WRITEDIARY') eq 'VAR') {
		my $url = 'writedialy.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_WRITEDIARY => &convertOutput($url));
	}

	# ���L��ǂނ� URL
	if ($tmpl->query(name => 'URL_READDIARY') eq 'VAR') {
		my $url = 'readdialy.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_READDIARY => &convertOutput($url));
	}

	# �����o�[�ꗗ�� URL
	if ($tmpl->query(name => 'URL_MEMBERLIST') eq 'VAR') {
		my $url = 'memberlist.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_MEMBERLIST => &convertOutput($url));
	}

	# �v���t�B�[���� URL
	if ($tmpl->query(name => 'URL_PROFILE') eq 'VAR') {
		my $url = 'profile.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_PROFILE => &convertOutput($url));
	}

	# �ݒ�ύX�� URL
	if ($tmpl->query(name => 'URL_OPTION') eq 'VAR') {
		my $url = 'option.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_OPTION => &convertOutput($url));
	}

	# �ȒP���O�C���ݒ�� URL
	if ($tmpl->query(name => 'URL_SETEASY') eq 'VAR') {
		my $url = 'seteasy.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_SETEASY => &convertOutput($url));
	}

	# �W�v�� URL
	if ($tmpl->query(name => 'URL_ADDUP') eq 'VAR' && $powerlevel >= 5) {
		my $url = 'addup.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_ADDUP => &convertOutput($url));
	}

	if ($tmpl->query(name => 'URL_SELFONTAMAIMAGE') eq 'VAR' || 
		$tmpl->query(name => 'SELFONTAMANAME') eq 'VAR' ||
		$tmpl->query(name => 'SELFONTAMAOWNERNAME') eq 'VAR') {
		if ($dbh && $session && $session->param('userid')) {
			# ���񂽂܎擾
			my %ontama = &getOntama($dbh, $session->param('userid'));
			# ���񂽂܉摜�� URL
			if ($ontama{'image'} && $tmpl->query(name => 'URL_SELFONTAMAIMAGE') eq 'VAR') {
				my $url = $config{'ontamaimagesurl'}.'/'.$ontama{'image'};
				$tmpl->param(URL_SELFONTAMAIMAGE => &convertOutput($url));
			}
			# ���񂽂܂̖��O
			if ($ontama{'name'} && $tmpl->query(name => 'SELFONTAMANAME') eq 'VAR') {
				$tmpl->param(SELFONTAMANAME => &convertOutput($ontama{'name'}));
			}
			# ���񂽂܂̎�����̖��O
			if ($ontama{'ownername'} && $tmpl->query(name => 'SELFONTAMAOWNERNAME') eq 'VAR') {
				$tmpl->param(SELFONTAMAOWNERNAME => &convertOutput($ontama{'ownername'}));
			}

			# ���񂽂܎��S�t���O
			if ($ontama{'health'} == 0 && $tmpl->query(name => 'SELFONTAMADEAD') eq 'VAR') {
				$tmpl->param(SELFONTAMADEAD => 1);
			}
		}
	}
	
	# ���񂽂܂� URL
	if ($tmpl->query(name => 'URL_ONTAMA') eq 'VAR') {
		my $url = 'ontama.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_ONTAMA => &convertOutput($url));
	}

	# ���񂽂܈ꗗ�� URL
	if ($tmpl->query(name => 'URL_ONTAMALIST') eq 'VAR') {
		my $url = 'ontamalist.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_ONTAMALIST => &convertOutput($url));
	}

	# ���񂽂܃}�j���A���� URL
	if ($tmpl->query(name => 'URL_ONTAMAMANUAL') eq 'VAR') {
		my $url = 'ontamamanual.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_ONTAMAMANUAL => &convertOutput($url));
	}

	# ���񂽂ܐݒ�� URL
	if ($tmpl->query(name => 'URL_SETONTAMA') eq 'VAR') {
		my $url = 'setontama.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_SETONTAMA => &convertOutput($url));
	}

	# ���O�A�E�g�� URL
	if ($tmpl->query(name => 'URL_LOGOUT') eq 'VAR') {
		my $url = 'logout.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_LOGOUT => &convertOutput($url));
	}

	# �z�[���� URL
	if ($tmpl->query(name => 'URL_HOME') eq 'VAR') {
		my $url = 'home.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_HOME => &convertOutput($url));
	}

	# ���[�����e�m�F�� URL
	if ($tmpl->query(name => 'URL_RECEIVEMAIL') eq 'VAR') {
		my $url = 'receivemail.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_RECEIVEMAIL => &convertOutput($url));
	}

	# �����ƐV������ URL
	if ($tmpl->query(name => 'URL_NEWS') eq 'VAR') {
		my $url = 'news.cgi';
		if ($isMobile && $session) {
			$url .= "?$sidurl";
		}
		$tmpl->param(URL_NEWS => &convertOutput($url));
	}

	# �g�ы@����
	if ($dbh && $session && $session->param('userid') && $tmpl->query(name => 'MOBCODE') eq 'VAR') {
		my $mobcode = &selectFetch($dbh, 'SELECT mobcode FROM users WHERE userid=? AND deleteflag=?', ($session->param('userid'), '0'));
		if ($mobcode) {
			$tmpl->param(MOBCODE => &convertOutput($mobcode));
		}
	}

	# �t�H�[�����ꗗ
	if ($dbh && $tmpl->query(name => 'FORUMCATEGORIES') eq 'LOOP') {
		my @forumcategories = ();
		my $sql = 'SELECT forumcategoryid, name FROM forumcategories WHERE deleteflag=? AND powerlevel<=? order by orderno';
		my @bind = ('0', $powerlevel);
		my @categoriesrows = &selectFetchArrayRef($dbh, $sql, @bind);
		foreach my $row(@categoriesrows) {
			my ($forumcategoryid, $name) = @$row;
			my %category = ();
			# �t�H�[�����J�e�S����
			if ($tmpl->query(name => ['FORUMCATEGORIES', 'NAME']) eq 'VAR') {
				$category{'NAME'} = &convertOutput($name);
			}
			# �t�H�[�����J�e�S��ID
			if ($tmpl->query(name => ['FORUMCATEGORIES', 'ID']) eq 'VAR') {
				$category{'ID'} = $forumcategoryid;
			}
			if ($tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS']) eq 'LOOP') {
				my @forums = ();
				my $sql = 'SELECT forumid, name, note FROM forums WHERE deleteflag=? AND forumcategoryid=? AND powerlevel<=? order by orderno';
				my @bind = ('0', $forumcategoryid, $powerlevel);
				my @forumsrows = &selectFetchArrayRef($dbh, $sql, @bind);
				foreach my $row(@forumsrows) {
					my ($forumid, $name, $note) = @$row;
					my %forum = ();
					# �t�H�[������
					if ($tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'NAME']) eq 'VAR') {
						$forum{'NAME'} = &convertOutput($name);
					}
					# �t�H�[��������
					if ($tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'NOTE']) eq 'VAR') {
						$forum{'NOTE'} = &convertOutput($note, 1);
					}
					# �t�H�[����URL
					if ($tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'URL']) eq 'VAR') {
						my $url = 'forum.cgi?forumid='.$forumid;
						if ($isMobile && $session) {
							$url .= "&$sidurl";
						}
						$forum{'URL'} = &convertOutput($url);
					}
					if ($tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'URL_LASTUSER']) eq 'VAR' || 
						$tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'LASTUSER']) eq 'VAR' || 
						$tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'LASTTIME']) eq 'VAR') {
						my $sql = 
							'SELECT a.lasttime, b.userid, b.name'.
							' FROM topics a, users b'.
							' WHERE a.lastuserid=b.userid AND a.deleteflag=? AND a.forumid=?'.
							' ORDER BY lasttime DESC LIMIT 0, 1';
						my @bind = ('0', $forumid);
						my ($lasttime, $userid, $username) = &selectFetchArray($dbh, $sql, @bind);
						# �ŏI���e��URL
						if ($userid && $tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'URL_LASTUSER']) eq 'VAR') {
							my $url = 'profile.cgi?userid='.$userid;
							if ($isMobile && $session) {
								$url .= "&$sidurl";
							}
							$forum{'URL_LASTUSER'} = &convertOutput($url);
						}
						# �ŏI���e�Җ�
						if ($username && $tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'LASTUSER']) eq 'VAR') {
							$forum{'LASTUSER'} = &convertOutput($username);
						}
						# �ŏI���e����
						if ($lasttime && $tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'LASTTIME']) eq 'VAR') {
							$forum{'LASTTIME'} = $lasttime;
						}
					}
					# �b�萔
					if ($tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'THREADCOUNT']) eq 'VAR') {
						my $sql = 
							'SELECT count(*)'.
							' FROM topics'.
							' WHERE deleteflag=? AND forumid=?';
						my @bind = ('0', $forumid);
						my ($count) = &selectFetchArray($dbh, $sql, @bind);
						$forum{'THREADCOUNT'} = $count;
					}
					# ���e��
					if ($tmpl->query(name => ['FORUMCATEGORIES', 'FORUMS', 'POSTCOUNT']) eq 'VAR') {
						my $sql = 
							'SELECT count(*)'.
							' FROM topiccomments'.
							' WHERE deleteflag=? AND forumid=?';
						my @bind = ('0', $forumid);
						my ($count) = &selectFetchArray($dbh, $sql, @bind);
						$forum{'POSTCOUNT'} = $count;
					}
					push(@forums, \%forum);
				}
				$category{'FORUMS'} = \@forums;
			}
			push(@forumcategories, \%category);
		}
		$tmpl->param(FORUMCATEGORIES=> \@forumcategories);
	}

	# �V���ꗗ
	if ($dbh && $tmpl->query(name => 'NEWS') eq 'LOOP') {
		my @newsvars = ();
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
			' ORDER BY a.lasttime DESC'.
			' LIMIT 0, 5';
		my @bind = ('0', '0', $powerlevel);
		my @rows = &selectFetchArrayRef($dbh, $sql, @bind);
		foreach my $row(@rows) {
			my ($forumid, $forumname, $topicid, $title, $lastcommentid, $lastuserid, $lastusername, $lasttime, $commentcount) = @$row;
			my %newsvar = ();
			# ����
			if ($tmpl->query(name => ['NEWS', 'TIME']) eq 'VAR') {
				$newsvar{'TIME'} = &convertOutput($lasttime);
			}
			# ���t
			if ($tmpl->query(name => ['NEWS', 'DATE']) eq 'VAR') {
				if ($lasttime =~ /^(\d{4})\-(\d{2})\-(\d{2}) /) {
					$newsvar{'DATE'} = &convertOutput($2.'��'.$3.'��');
				}
			}
			# �g�s�b�N�^�C�g��
			if ($tmpl->query(name => ['NEWS', 'TOPICTITLE']) eq 'VAR') {
				$newsvar{'TOPICTITLE'} = &convertOutput($title);
			}
			# �g�s�b�NURL
			if ($tmpl->query(name => ['NEWS', 'URL']) eq 'VAR') {
				my $url = 'topic.cgi?';
				if ($lastcommentid) {
					$url .= 'topiccommentid='.$lastcommentid;
				} else {
					$url .= 'topicid='.$topicid;
				}
				if ($isMobile && $session) {
					$url .= "&$sidurl";
				}
				if ($lastcommentid) {
					$url .= '#'.$lastcommentid;
				}
				$newsvar{'URL'} = &convertOutput($url);
			}
			# �g�s�b�N�R�����g��
			if ($tmpl->query(name => ['NEWS', 'COUNT']) eq 'VAR') {
				$newsvar{'COUNT'} = &convertOutput($commentcount);
			}
			# �t�H�[������
			if ($tmpl->query(name => ['NEWS', 'FORUMNAME']) eq 'VAR') {
				$newsvar{'FORUMNAME'} = &convertOutput($forumname);
			}
			# �t�H�[����URL
			if ($tmpl->query(name => ['NEWS', 'FORUMURL']) eq 'VAR') {
				my $url = 'forum.cgi?topicid='.$topicid;
				if ($isMobile && $session) {
					$url .= "&$sidurl";
				}
				$url .= '#'.$topicid;
				$newsvar{'FORUMURL'} = &convertOutput($url);
			}
			# �ŏI���e��
			if ($tmpl->query(name => ['NEWS', 'LASTUSERNAME']) eq 'VAR') {
				$newsvar{'LASTUSERNAME'} = &convertOutput($lastusername);
			}
			# �ŏI���e��URL
			if ($tmpl->query(name => ['NEWS', 'LASTUSERURL']) eq 'VAR') {
				my $url = 'profile.cgi?userid='.$lastuserid;
				if ($isMobile && $session) {
					$url .= "&$sidurl";
				}
				$newsvar{'LASTUSERURL'} = &convertOutput($url);
			}
			push(@newsvars, \%newsvar);
		}
		$tmpl->param(NEWS=> \@newsvars);
	}

	# �V�����b�Z�[�W�̌���
	if ($dbh && $session && $session->param('userid') && $tmpl->query(name => 'NEW_MESSAGE_COUNT') eq 'VAR') {
		my $count = &selectFetch($dbh, 'SELECT count(*) FROM messages WHERE receiver_userid=? AND receiver_deleteflag=? AND opentime IS NULL', ($session->param('userid'), '0'));
		if ($count) {
			$tmpl->param(NEW_MESSAGE_COUNT => $count);
		}
	}

	# �V�����o�^���������o�[�ꗗ
	if ($dbh && $tmpl->query(name => 'NEWMEMBERS') eq 'LOOP') {
		my @newmembersvars = ();
		my $sql = 
			'SELECT'.
			' userid,'.
			' name,'.
			' registtime'.
			' FROM'.
			' users'.
			' WHERE'.
			' deleteflag=?'.
			' AND registtime >= DATE_ADD(CURRENT_DATE, INTERVAL ? MONTH)'.
			' ORDER BY registtime DESC'.
			' LIMIT 0, 5';
		my @bind = ('0', -1);
		my @rows = &selectFetchArrayRef($dbh, $sql, @bind);
		foreach my $row(@rows) {
			my ($userid, $name, $registtime) = @$row;
			my %newmembersvar = ();
			# ����
			if ($tmpl->query(name => ['NEWMEMBERS', 'TIME']) eq 'VAR') {
				$newmembersvar{'TIME'} = &convertOutput($registtime);
			}
			# ���t
			if ($tmpl->query(name => ['NEWMEMBERS', 'DATE']) eq 'VAR') {
				if ($registtime =~ /^(\d{4})\-(\d{2})\-(\d{2}) /) {
					$newmembersvar{'DATE'} = &convertOutput($2.'��'.$3.'��');
				}
			}
			# ���O
			if ($tmpl->query(name => ['NEWMEMBERS', 'NAME']) eq 'VAR') {
				$newmembersvar{'NAME'} = &convertOutput($name);
			}
			# �����o�[URL
			if ($tmpl->query(name => ['NEWMEMBERS', 'URL']) eq 'VAR') {
				my $url = 'profile.cgi?userid='.$userid;
				if ($isMobile && $session) {
					$url .= "&$sidurl";
				}
				$newmembersvar{'URL'} = &convertOutput($url);
			}
			push(@newmembersvars, \%newmembersvar);
		}
		$tmpl->param(NEWMEMBERS => \@newmembersvars);
	}


	# ���݃I�����C���̃����o�[�ꗗ
	if ($dbh && $tmpl->query(name => 'ONLINEMEMBERS') eq 'LOOP') {
		my @onlinemembersvars = ();
		my $sql = 
			'SELECT'.
			' a.userid,'.
			' a.name,'.
			' b.registtime,'.
			' b.title'.
			' FROM'.
			' users a,'.
			' onlineusers b'.
			' WHERE'.
			' a.userid=b.userid'.
			' AND a.deleteflag=?'.
			' AND b.deleteflag=?'.
			' ORDER BY registtime DESC'.
			' LIMIT 0, 5';
		my @bind = ('0', '0');
		my @rows = &selectFetchArrayRef($dbh, $sql, @bind);
		foreach my $row(@rows) {
			my ($userid, $name, $registtime, $title) = @$row;
			my %onlinemembersvar = ();
			# ���O
			if ($tmpl->query(name => ['ONLINEMEMBERS', 'NAME']) eq 'VAR') {
				$onlinemembersvar{'NAME'} = &convertOutput($name);
			}
			# �����o�[URL
			if ($tmpl->query(name => ['ONLINEMEMBERS', 'URL']) eq 'VAR') {
				my $url = 'profile.cgi?userid='.$userid;
				if ($isMobile && $session) {
					$url .= "&$sidurl";
				}
				$onlinemembersvar{'URL'} = &convertOutput($url);
			}
			# �����o�[URL
			if ($tmpl->query(name => ['ONLINEMEMBERS', 'PAGETITLE']) eq 'VAR') {
				$onlinemembersvar{'PAGETITLE'} = &convertOutput($title);
			}
			push(@onlinemembersvars, \%onlinemembersvar);
		}
		$tmpl->param(ONLINEMEMBERS => \@onlinemembersvars);
	}


	return $msg;
}


1;
