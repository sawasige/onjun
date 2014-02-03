#!/usr/bin/perl -w
require './global.pl';
use strict; # �ϐ��錾�K�{
use CGI::Carp qw(fatalsToBrowser); # �G���[���b�Z�[�W��\������i���Ȃ��ꍇ�R�����g�A�E�g�j
use DBI;

# �ϐ�
my $cgi;
my %config;
my @msgs = ();

#�v���O�����J�n
&main;

##########
# ���C��
sub main {
	$cgi = new CGI;

	# �ݒ�ǂݍ���
	%config = &config;

	# �e�[�u���쐬
	&createTable;

	# ��ʕ\��
	&disp;
}

###########
# ��ʕ\��
sub disp {
	# �e���v���[�g�ǂݍ���
	#my $tmpl = HTML::Template->new(filename => $config{'templatedir'}.'/index.tmpl');
	my $tmpl = &readTemplate($cgi);

	# �^�C�g��
	if ($tmpl->query(name => 'TITLE') eq 'VAR') {
		$tmpl->param(TITLE => $config{'title'});
	}
	
	# �T�u�^�C�g��
	if ($tmpl->query(name => 'SUBTITLE') eq 'VAR') {
		$tmpl->param(SUBTITLE => $config{'subtitle'});
	}

	# �C���X�g�[�����O
	if ($tmpl->query(name => 'INSTALLLOG') eq 'LOOP') {
		my @installlog = ();
		foreach my $msg(@msgs) {
			my %log;
			$log{'VALUE'} = $msg;
			push(@installlog, \%log);
		}
		$tmpl->param(INSTALLLOG => \@installlog);
	}
	
	my $output = $tmpl->output;
	# �S�p�𔼊p��
	#jcode::z2h_sjis(\$output);

	print $cgi->header(-charset=>'Shift_JIS');
	print $output;
	
}

###########
# ��ʕ\��
sub createTable {
	my $dbh = &connectDB(0);

	# users �e�[�u��
	push(@msgs, '[users] �e�[�u���쐬�J�n');
	my $sql_users = <<END;
CREATE TABLE users (
 userid int(10) unsigned NOT NULL auto_increment,
 deleteflag char(1) NOT NULL default '0',
 powerlevel int(1) NOT NULL default 1,
 name varchar(30) NOT NULL default '',
 pass varchar(30) NOT NULL default '',
 mail varchar(60) NOT NULL default '',
 mobcode varchar(30) NOT NULL default '',
 useragent varchar(255) NOT NULL default '',
 realname varchar(60) NOT NULL default '',
 url varchar(100) NOT NULL default '',
 birthday date NOT NULL default '',
 sex char(1) NOT NULL default '',
 blood varchar(2) NOT NULL default '',
 job varchar(60) NOT NULL default '',
 part varchar(60) NOT NULL default '',
 place varchar(60) NOT NULL default '',
 age int(3) NOT NULL default 0,
 note text NOT NULL,
 mailsid varchar(60) NOT NULL default '',
 mailmessageflag char(1) NOT NULL default '1',
 registtime datetime NOT NULL default '',
 lasttime datetime NOT NULL default '',
 PRIMARY KEY (userid),
 UNIQUE KEY name (name)
) TYPE=MyISAM
END
	if ($dbh->do($sql_users)) {
		push(@msgs, '[users] �e�[�u���쐬����');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}
	
	# �Ǘ����[�U�[�쐬
	push(@msgs, '�Ǘ����[�U�[�쐬');
	my @admindata = (1, 5, $config{'initadminname'}, $config{'initadminpass'}, $config{'initadminmail'}, $config{'initadminmobcode'});
	if ($dbh->do('INSERT INTO users(userid, powerlevel, name, pass, mail, mobcode, registtime) VALUES(?, ?, ?, ?, ?, ?, now())', undef, @admindata)) {
		push(@msgs, '�Ǘ����[�U�[�쐬����');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}



# messages �e�[�u��
	push(@msgs, '[messages] �e�[�u���쐬�J�n');
	my $sql_parts = <<END;
CREATE TABLE messages (
 messageid int(10) unsigned NOT NULL auto_increment,
 replyid int(10) unsigned NOT NULL default 0,
 sender_userid int(10) NOT NULL default 0,
 receiver_userid int(10) NOT NULL default 0,
 subject varchar(255) NOT NULL default '',
 body text NOT NULL,
 sender_deleteflag char(1) NOT NULL default '0',
 receiver_deleteflag char(1) NOT NULL default '0',
 sendtime datetime NOT NULL,
 opentime datetime,
 PRIMARY KEY (messageid)
) TYPE=MyISAM
END
	if ($dbh->do($sql_parts)) {
		push(@msgs, '[messages] �e�[�u���쐬����');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}


# forumcategories �e�[�u��
	push(@msgs, '[forumcategories] �e�[�u���쐬�J�n');
	my $sql_parts = <<END;
CREATE TABLE forumcategories (
 forumcategoryid int(3) unsigned NOT NULL auto_increment,
 deleteflag char(1) NOT NULL default '0',
 name varchar(255) NOT NULL default '',
 powerlevel int(1) NOT NULL default 1,
 orderno int(3) NOT NULL default 0,
 PRIMARY KEY (forumcategoryid)
) TYPE=MyISAM
END
	if ($dbh->do($sql_parts)) {
		push(@msgs, '[forumcategories] �e�[�u���쐬����');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}
	# �t�H�[�����J�e�S���쐬
	push(@msgs, '�t�H�[�����J�e�S���쐬');
	my $sql = 'INSERT INTO forumcategories(forumcategoryid, name, powerlevel, orderno) VALUES(?, ?, ?, ?)';
	my $sth = $dbh->prepare($sql);
	if ($sth) {
		my @bind;
		@bind = (1, '���S�җp', 1, 1);
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���S�җp�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (2, '��ʗp', 1, 2);
		if ($sth->execute(@bind)) {
			push(@msgs, '�u��ʗp�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (3, '�Ǘ��җp', 5, 3);
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�Ǘ��җp�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}

# forums �e�[�u��
	push(@msgs, '[forums] �e�[�u���쐬�J�n');
	my $sql_parts = <<END;
CREATE TABLE forums (
 forumid int(5) unsigned NOT NULL auto_increment,
 deleteflag char(1) NOT NULL default '0',
 forumcategoryid int(3) unsigned NOT NULL default 0,
 name varchar(255) NOT NULL default '',
 note text NOT NULL,
 powerlevel int(1) NOT NULL default 1,
 orderno int(10) NOT NULL default 0,
 PRIMARY KEY (forumid)
) TYPE=MyISAM
END
	if ($dbh->do($sql_parts)) {
		push(@msgs, '[forums] �e�[�u���쐬����');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}
	# �t�H�[�����쐬
	push(@msgs, '�t�H�[�����쐬');
	my $sql = 'INSERT INTO forums(forumid, forumcategoryid, name, note, powerlevel, orderno) VALUES(?, ?, ?, ?, ?, ?)';
	my $sth = $dbh->prepare($sql);
	if ($sth) {
		my @bind;
		@bind = (1, 1, '�悤�����I', '�V�K�o�^�̕��͂��̃t�H�[�����ŁA���ȏЉ�₱�̃T�C�g��m���������������C�y�ɏ�������ł��������B', 1, 1);
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�悤�����I�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (2, 1, 'onjun �ɂ���', 'onjun �̎g�������킩��Ȃ��ꍇ�̎����A�������ق����ǂ��ӏ��Ȃǂ̕񍐁^��Ăɂ����p���������B', 1, 2);
		if ($sth->execute(@bind)) {
			push(@msgs, '�uonjun �ɂ��āv�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (3, 2, '�G�k', '���Ƀe�[�}�����߂��ɁA�G�k���ɂ����p���������B', 1, 1);
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�G�k�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (4, 2, '�ߋ���', '�����̋ߋ��A���̐l�̋ߋ��ȂǂŁA�m���Ă�����A�m�肽�����Ȃǂ���������ł��������B', 1, 2);
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ߋ��񍐁v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (5, 2, '������', '���Ȃ��̂��E�ߏ���m�肽��������������ł��������B�����̂��ƁA�玙�̂��ƁA�p�\�R���A���s�A��̂��ƂȂǉ��ł� OK �I', 1, 3);
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�������v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (6, 3, '�Ǘ��ҏ�����', '�Ǘ��җp�̃t�H�[�����ł��B��ʃ��[�U�[�͏������݂��{�����ł��܂���B', 5, 1);
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�Ǘ��ҏ������v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}


# topics �e�[�u��
	push(@msgs, '[topics] �e�[�u���쐬�J�n');
	my $sql_parts = <<END;
CREATE TABLE topics (
 topicid int(10) unsigned NOT NULL auto_increment,
 deleteflag char(1) NOT NULL default '0',
 forumid int(5) unsigned NOT NULL default 0,
 title varchar(255) NOT NULL default '',
 body text NOT NULL,
 registuserid int(10) unsigned NOT NULL default 0,
 registtime datetime NOT NULL,
 lastcommentid int(10) unsigned NOT NULL default 0,
 lastuserid int(10) unsigned NOT NULL default 0,
 lasttime datetime NOT NULL,
 commentcount int(10) unsigned NOT NULL default 0,
 PRIMARY KEY (topicid)
) TYPE=MyISAM
END
	if ($dbh->do($sql_parts)) {
		push(@msgs, '[topics] �e�[�u���쐬����');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}


# topiccomments �e�[�u��
	push(@msgs, '[topiccomments] �e�[�u���쐬�J�n');
	my $sql_parts = <<END;
CREATE TABLE topiccomments (
 topiccommentid int(10) unsigned NOT NULL auto_increment,
 deleteflag char(1) NOT NULL default '0',
 forumid int(5) unsigned NOT NULL default 0,
 topicid int(10) unsigned NOT NULL default 0,
 body text NOT NULL,
 registuserid int(10) unsigned NOT NULL default 0,
 registtime datetime NOT NULL,
 PRIMARY KEY (topiccommentid)
) TYPE=MyISAM
END
	if ($dbh->do($sql_parts)) {
		push(@msgs, '[topiccomments] �e�[�u���쐬����');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}

# mailkeys �e�[�u��
	push(@msgs, '[mailkeys] �e�[�u���쐬�J�n');
	my $sql_parts = <<END;
CREATE TABLE mailkeys (
 mailkeyid int(10) unsigned NOT NULL auto_increment,
 deleteflag char(1) NOT NULL default '0',
 kind char(2) NOT NULL default '',
 id int(10) unsigned NOT NULL default 0,
 keystr varchar(5) NOT NULL default '',
 registuserid int(10) unsigned NOT NULL default 0,
 registtime datetime NOT NULL,
 PRIMARY KEY (mailkeyid)
) TYPE=MyISAM
END
	if ($dbh->do($sql_parts)) {
		push(@msgs, '[mailkeys] �e�[�u���쐬����');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}

# onlineusers �e�[�u��
	push(@msgs, '[onlineusers] �e�[�u���쐬�J�n');
	my $sql_parts = <<END;
CREATE TABLE onlineusers (
 userid int(10) unsigned NOT NULL default 0,
 deleteflag char(1) NOT NULL default '0',
 registtime datetime NOT NULL,
 title varchar(255) NOT NULL default '',
 PRIMARY KEY (userid)
) TYPE=MyISAM
END
	if ($dbh->do($sql_parts)) {
		push(@msgs, '[onlineusers] �e�[�u���쐬����');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}


# addup �e�[�u��
	push(@msgs, '[addup] �e�[�u���쐬�J�n');
	my $sql_parts = <<END;
CREATE TABLE addup (
 userid int(10) unsigned NOT NULL default 0,
 messagecount int(10) unsigned NOT NULL default 0,
 topiccount int(10) unsigned NOT NULL default 0,
 topiccommentcount int(10) unsigned NOT NULL default 0,
 PRIMARY KEY (userid)
) TYPE=MyISAM
END
	if ($dbh->do($sql_parts)) {
		push(@msgs, '[addup] �e�[�u���쐬����');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}




# ontama �e�[�u��
	push(@msgs, '[ontama] �e�[�u���쐬�J�n');
	my $sql_parts = <<END;
CREATE TABLE ontama (
 ontamaid int(10) unsigned NOT NULL default 0,
 parentid int(10) unsigned NOT NULL default 0,
 image varchar(20) NOT NULL default '',
 maxgrow int(10) unsigned NOT NULL default 0,
 healthdiff int(3) unsigned NOT NULL default 0,
 hungrydiff int(3) unsigned NOT NULL default 0,
 happydiff int(3) unsigned NOT NULL default 0,
 diarypercent int(3) unsigned NOT NULL default 0,
 analyzepercent int(3) unsigned NOT NULL default 0,
 PRIMARY KEY (ontamaid)
) TYPE=MyISAM
END
	if ($dbh->do($sql_parts)) {
		push(@msgs, '[ontama] �e�[�u���쐬����');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}

	# ontama �L�����N�^�[�쐬
	push(@msgs, 'ontama �L�����N�^�[�쐬');
	my $sql = 'INSERT INTO ontama(ontamaid, parentid, image, maxgrow, healthdiff, hungrydiff, happydiff, diarypercent, analyzepercent) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)';
	my $sth = $dbh->prepare($sql);
	if ($sth) {
		my @bind;
		@bind = (1, 0, 'egg1.gif', 15, 0, 0, 0, 50, 0);
		if ($sth->execute(@bind)) {
			push(@msgs, '�uegg1.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (2, 1, 'egg2.gif', 20, 0, 0, 0, 50, 0);
		if ($sth->execute(@bind)) {
			push(@msgs, '�uegg2.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (3, 2, 'baby1.gif', 40, 5, 5, 5, 10, 0);
		if ($sth->execute(@bind)) {
			push(@msgs, '�ubaby1.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (4, 2, 'baby2.gif', 40, 5, 5, 5, 10, 0);
		if ($sth->execute(@bind)) {
			push(@msgs, '�ubaby2.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (5, 3, 'bug1.gif', 80, 10, 10, 7, 30, 10);
		if ($sth->execute(@bind)) {
			push(@msgs, '�ubug1.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (6, 3, 'bug2.gif', 80, 10, 10, 7, 30, 10);
		if ($sth->execute(@bind)) {
			push(@msgs, '�ubug2.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (7, 4, 'bug3.gif', 80, 10, 10, 7, 30, 10);
		if ($sth->execute(@bind)) {
			push(@msgs, '�ubug3.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (8, 4, 'bug4.gif', 80, 10, 10, 7, 30, 10);
		if ($sth->execute(@bind)) {
			push(@msgs, '�ubug4.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (9, 5, 'pupa1.gif', 120, 10, 15, 10, 50, 15);
		if ($sth->execute(@bind)) {
			push(@msgs, '�upupa1.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (10, 5, 'pupa2.gif', 120, 10, 15, 10, 50, 15);
		if ($sth->execute(@bind)) {
			push(@msgs, '�upupa2.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (11, 6, 'pupa3.gif', 120, 10, 15, 10, 50, 15);
		if ($sth->execute(@bind)) {
			push(@msgs, '�upupa3.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (12, 6, 'pupa4.gif', 120, 10, 15, 10, 50, 15);
		if ($sth->execute(@bind)) {
			push(@msgs, '�upupa4.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (13, 7, 'pupa5.gif', 120, 10, 15, 10, 50, 15);
		if ($sth->execute(@bind)) {
			push(@msgs, '�upupa5.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (14, 7, 'pupa6.gif', 120, 10, 15, 10, 50, 15);
		if ($sth->execute(@bind)) {
			push(@msgs, '�upupa6.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (15, 8, 'pupa7.gif', 120, 10, 15, 10, 50, 15);
		if ($sth->execute(@bind)) {
			push(@msgs, '�upupa7.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (16, 8, 'pupa8.gif', 120, 10, 15, 10, 50, 15);
		if ($sth->execute(@bind)) {
			push(@msgs, '�upupa8.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (17, 9, 'imago1.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '�uimago1.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (18, 9, 'imago2.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '�uimago2.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (19, 10, 'imago3.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '�uimago3.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (20, 10, 'imago4.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '�uimago4.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (21, 11, 'imago5.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '�uimago5.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (22, 11, 'imago6.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '�uimago6.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (23, 12, 'imago7.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '�uimago7.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (24, 12, 'imago8.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '�uimago8.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (25, 13, 'imago9.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '�uimago9.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (26, 13, 'imago10.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '�uimago10.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (27, 14, 'imago11.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '�uimago11.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (28, 14, 'imago12.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '�uimago12.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (29, 15, 'imago13.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '�uimago13.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (30, 15, 'imago14.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '�uimago14.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (31, 16, 'imago15.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '�uimago15.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (32, 16, 'imago16.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '�uimago16.gif�v�쐬����');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}



# ontamausers �e�[�u��
	push(@msgs, '[ontamausers] �e�[�u���쐬�J�n');
	my $sql_parts = <<END;
CREATE TABLE ontamausers (
 userid int(10) unsigned NOT NULL default 0,
 ontamaid int(10) unsigned NOT NULL default 0,
 name varchar(30) NOT NULL default '',
 image varchar(20) NOT NULL default '',
 days int(5) unsigned NOT NULL default 0,
 level int(3) unsigned NOT NULL default 0,
 grow int(10) unsigned NOT NULL default 0,
 health int(3) unsigned NOT NULL default 0,
 hungry int(3) unsigned NOT NULL default 0,
 happy int(3) unsigned NOT NULL default 0,
 food int(3) unsigned NOT NULL default 0,
 growdate date NOT NULL default '',
 registtime datetime NOT NULL default '',
 lasttime datetime NOT NULL default '',
 PRIMARY KEY (userid)
) TYPE=MyISAM
END
	if ($dbh->do($sql_parts)) {
		push(@msgs, '[ontamausers] �e�[�u���쐬����');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}

# ontamastatus �e�[�u��
	push(@msgs, '[ontamastatus] �e�[�u���쐬�J�n');
	my $sql_parts = <<END;
CREATE TABLE ontamastatus (
 ontamastatusid int(10)  unsigned NOT NULL auto_increment,
 userid int(10) unsigned NOT NULL default 0,
 body text NOT NULL,
 registtime datetime NOT NULL default '',
 PRIMARY KEY (ontamastatusid)
) TYPE=MyISAM
END
	if ($dbh->do($sql_parts)) {
		push(@msgs, '[ontamastatus] �e�[�u���쐬����');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}

# ontamalogs �e�[�u��
	push(@msgs, '[ontamalogs] �e�[�u���쐬�J�n');
	my $sql_parts = <<END;
CREATE TABLE ontamalogs (
 ontamalogid int(10) unsigned NOT NULL auto_increment,
 userid int(10) unsigned NOT NULL default 0,
 body text NOT NULL,
 registtime datetime NOT NULL default '',
 PRIMARY KEY (ontamalogid)
) TYPE=MyISAM
END
	if ($dbh->do($sql_parts)) {
		push(@msgs, '[ontamalogs] �e�[�u���쐬����');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}

# ontamascripts �e�[�u��
	push(@msgs, '[ontamascripts] �e�[�u���쐬�J�n');
	my $sql_parts = <<END;
CREATE TABLE ontamascripts (
 ontamascriptid int(10) unsigned NOT NULL default 0,
 ontamaid int(10) unsigned NOT NULL default 0,
 body text NOT NULL,
 PRIMARY KEY (ontamascriptid)
) TYPE=MyISAM
END
	if ($dbh->do($sql_parts)) {
		push(@msgs, '[ontamascripts] �e�[�u���쐬����');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}

	# ontama ����Ӎ쐬
	push(@msgs, 'ontama ����Ӎ쐬');
	my $sql = 'INSERT INTO ontamascripts(ontamascriptid, ontamaid, body) VALUES(?, ?, ?)';
	my $sth = $dbh->prepare($sql);
	if ($sth) {
		my @bind;
		@bind = (1, 1, '�E�E�E�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�E�E�E�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (2, 1, '�X���X���c�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�X���X���c�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (3, 1, 'ZZZZ...�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�uZZZZ...�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (4, 2, '�I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (5, 2, '�~�V�b�I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�~�V�b�I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (6, 2, '�y�L�y�L�b�I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�y�L�y�L�b�I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (7, 2, '�ӂ񂪁[�I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ӂ񂪁[�I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (8, 2, '�ނ����������I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ނ����������I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (9, 3, '�̂ف`��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�̂ف`��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (10, 3, '�̂炽���`��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�̂炽���`��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (11, 3, '�����[�I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����[�I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (12, 3, '�������Ă����ӂ������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�������Ă����ӂ������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (13, 3, '�X���C���ɂ܂�����ꂽ�B���ꂢ���ȁB�v���v���I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�X���C���ɂ܂�����ꂽ�B���ꂢ���ȁB�v���v���I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (14, 4, '����`��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u����`��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (15, 4, '�������`��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�������`��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (16, 4, '���[�I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���[�I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (17, 4, '��������������������������');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���������������������������v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (18, 4, '�˂΂˂΁B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�˂΂˂΁B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (19, 5, '�����͂����B���邯���邯�[�I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����͂����B���邯���邯�[�I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (20, 5, '�Ђ���Ƃ��Ăނ�����Ă�H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�Ђ���Ƃ��Ăނ�����Ă�H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (21, 5, '�����H�āH�Ђ��H����������H���Ă����ꂽ�B�Ȃ�Ȃ񂾂낤�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����H�āH�Ђ��H����������H���Ă����ꂽ�B�Ȃ�Ȃ񂾂낤�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (22, 5, '�n�Q���Ă���ꂽ�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�n�Q���Ă���ꂽ�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (23, 5, '���킢�������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���킢�������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (24, 6, '�т��͂����I�������[�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�т��͂����I�������[�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (25, 6, '���傤�������߂�Ȃ����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���傤�������߂�Ȃ����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (26, 6, '���A�܂��������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���A�܂��������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (27, 6, '���񂤂�B��������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���񂤂�B��������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (28, 6, '�����Ă��ɂ��݂����ȁB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����Ă��ɂ��݂����ȁB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (29, 7, '�����H�Ђ��H�͂Ȃ��H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����H�Ђ��H�͂Ȃ��H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (30, 7, '�����͂�����[���񂾁B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����͂�����[���񂾁B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (31, 7, '���񂷂������Ă���ꂽ�B���񂷂��āH');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���񂷂������Ă���ꂽ�B���񂷂��āH�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (32, 7, '���͂�����������');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���͂������������v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (33, 7, '������������ɂɂ�܂ꂽ�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u������������ɂɂ�܂ꂽ�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (34, 8, '����������H�Ђ��H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u����������H�Ђ��H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (35, 8, '�͂񂩂����Ƃ����B���ꂩ�Ђ���Ă���邩�ȁc�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�͂񂩂����Ƃ����B���ꂩ�Ђ���Ă���邩�ȁc�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (36, 8, '�܂��ɂ��������傯��߂����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�܂��ɂ��������傯��߂����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (37, 8, '���傤�͂����������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���傤�͂����������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (38, 8, '�������͂������̂������ӂ����炨���₪��������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�������͂������̂������ӂ����炨���₪��������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (39, 9, '���ǂ邠�ق��ɂ݂邠�ق��A���Ȃ����ق��Ȃ炨�ǂ�ɂႻ�񂻂�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���ǂ邠�ق��ɂ݂邠�ق��A���Ȃ����ق��Ȃ炨�ǂ�ɂႻ�񂻂�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (40, 9, '�ӂ��񂫁��Ȃ����ւ񂩂�ł��Ȃ��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ӂ��񂫁��Ȃ����ւ񂩂�ł��Ȃ��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (41, 9, '�P�����ĂȂ������B�т���ʂ�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�P�����ĂȂ������B�т���ʂ�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (42, 9, '���Ă��~�߃N���[���ʂ肽�������̂ň��S���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���Ă��~�߃N���[���ʂ肽�������̂ň��S���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (43, 9, '����ɂႭ�[���[���ăJ�����[�Ȃ��̂��ȁH ���܂�����J�����[���肻������ˁB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u����ɂႭ�[���[���ăJ�����[�Ȃ��̂��ȁH ���܂�����J�����[���肻������ˁB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (44, 9, '�j���e���h�[���ăl�[���Z���X�Ȃ���ˁB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�j���e���h�[���ăl�[���Z���X�Ȃ���ˁB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (45, 9, '�ǂ������ăl�[���Z���X���w������ˁB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ǂ������ăl�[���Z���X���w������ˁB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (46, 9, '�������ǂ��������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�������ǂ��������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (47, 10, '�^�R�n�C���ă`���[�n�C���������̂����Ă�H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�^�R�n�C���ă`���[�n�C���������̂����Ă�H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (48, 10, '�E�E�E�����E�E�E�n�C�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�E�E�E�����E�E�E�n�C�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (49, 10, '���������Ă���������ˁB���܂蔄���ĂȂ����ǁB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���������Ă���������ˁB���܂蔄���ĂȂ����ǁB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (50, 10, '�ΐ��l���Ă���̂��ȁH');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ΐ��l���Ă���̂��ȁH�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (51, 10, '�^�R�̃X�~�͂��������Ȃ���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�^�R�̃X�~�͂��������Ȃ���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (52, 10, '�C�J�����^�R�B�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�C�J�����^�R�B�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (53, 10, '�����Ă��͋₾���Ɍ���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����Ă��͋₾���Ɍ���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (54, 10, '���ΏĂ��������[�I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���ΏĂ��������[�I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (55, 11, '�΂����΂����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�΂����΂����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (56, 11, '�M�����I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�M�����I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (57, 11, '�N���b�s�[�I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�N���b�s�[�I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (58, 11, '���������Α��ǂ��������H�ǂ�����Ē������悤�c�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���������Α��ǂ��������H�ǂ�����Ē������悤�c�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (59, 11, '���������肵�āB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���������肵�āB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (60, 11, '�E���g���̕�H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�E���g���̕�H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (61, 11, '�V���͂���܂���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�V���͂���܂���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (62, 11, '�����ĂȂ������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����ĂȂ������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (63, 12, '�ɂ��ɂ��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ɂ��ɂ��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (64, 12, '���I�肪�Ȃ��I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���I�肪�Ȃ��I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (65, 12, '���I�����Ȃ��I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���I�����Ȃ��I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (66, 12, '�d�b�������Ǐo�Ȃ������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�d�b�������Ǐo�Ȃ������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (67, 12, '�����Z�Ȃ瓾�ӁB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����Z�Ȃ瓾�ӁB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (68, 12, '���͂�������������������������������');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���͂��������������������������������v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (69, 12, '��������Ǝv���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u��������Ǝv���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (70, 12, '���������c�������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���������c�������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (71, 13, '��͌����܂���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u��͌����܂���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (72, 13, '���̕s�����i�E���ł���H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���̕s�����i�E���ł���H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (73, 13, '�Ȃ�قǁI��������AI���ӂ邦�܂����I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�Ȃ�قǁI��������AI���ӂ邦�܂����I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (74, 13, '�݂��̂ǂɋl�܂点�Ď��񂾂�A�݂������̂ł��傤���H ����Ƃ��̂ǁH');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�݂��̂ǂɋl�܂点�Ď��񂾂�A�݂������̂ł��傤���H ����Ƃ��̂ǁH�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (75, 13, '�P���`�N�ƃE���`�N���V�i�`�N�Ƃ���Ȋ֌W���������Ȃ�āB���Ȃǂ�Ȃ��ˁB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�P���`�N�ƃE���`�N���V�i�`�N�Ƃ���Ȋ֌W���������Ȃ�āB���Ȃǂ�Ȃ��ˁB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (76, 13, '�M�\�������B�t�����I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�M�\�������B�t�����I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (77, 13, '���̑O�͉̂z���s�ׂł����B���݂܂���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���̑O�͉̂z���s�ׂł����B���݂܂���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (78, 13, '��X�����̓J�[�̂��Ƃł��B�J�[�͂܂�т傤�̂��Ƃł��B�܂�т傤�͂܂�ڂ����͂邩�Ɋ댯�ł��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u��X�����̓J�[�̂��Ƃł��B�J�[�͂܂�т傤�̂��Ƃł��B�܂�т傤�͂܂�ڂ����͂邩�Ɋ댯�ł��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (79, 14, '���킢�����Ȏq���ɐ��̂𖾂����������������悤�Ƃ��܂����B�ł�������ꂿ�Ⴂ�܂����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���킢�����Ȏq���ɐ��̂𖾂����������������悤�Ƃ��܂����B�ł�������ꂿ�Ⴂ�܂����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (80, 14, '�q�����Ăǂ�����Ă���̂��ȁH �h���b�O�A���h�h���b�v�ŃR�s�[�ł���H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�q�����Ăǂ�����Ă���̂��ȁH �h���b�O�A���h�h���b�v�ŃR�s�[�ł���H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (81, 14, '�^�b�v�_���X���͂��߂܂����B���S�҂Ƃ͎v���Ȃ��ƕ]���ł��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�^�b�v�_���X���͂��߂܂����B���S�҂Ƃ͎v���Ȃ��ƕ]���ł��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (82, 14, '����񂱂Ƃ����߂�ڂ́u�񂱁v�́u�����v�݂����Ȃ��́HKABA.�񂱁B�G�r�񂱁B�Ȃ񂩃��_�B�Q�񂱂˂�B��H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u����񂱂Ƃ����߂�ڂ́u�񂱁v�́u�����v�݂����Ȃ��́HKABA.�񂱁B�G�r�񂱁B�Ȃ񂩃��_�B�Q�񂱂˂�B��H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (83, 14, '�Y�b�V���h�b�V���I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�Y�b�V���h�b�V���I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (84, 14, '������ۂ��悤�I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u������ۂ��悤�I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (85, 14, '������ۂ�����Ƃ��킩��Ȃ��Ȃ�܂����B�Əo���Ă���Ȃ��񂶁H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u������ۂ�����Ƃ��킩��Ȃ��Ȃ�܂����B�Əo���Ă���Ȃ��񂶁H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (86, 14, 'O�r�̒����������Ă�H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�uO�r�̒����������Ă�H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (87, 15, '�j���[���[�N�̓��̂ق��ɍs�����B�q���ƂȂ��悭�Ȃ�����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�j���[���[�N�̓��̂ق��ɍs�����B�q���ƂȂ��悭�Ȃ�����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (88, 15, '���]�ԂƂ΂��Ă݂��B�����������΂��ȁB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���]�ԂƂ΂��Ă݂��B�����������΂��ȁB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (89, 15, '���̓�����������B�ق��̕����͂���Ȃ����炷�Ă���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���̓�����������B�ق��̕����͂���Ȃ����炷�Ă���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (90, 15, '���ɂ炭��������������I���ւ��I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���ɂ炭��������������I���ւ��I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (91, 15, '�厖�����������I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�厖�����������I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (92, 15, '�܂��A�ӂ����ˁB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�܂��A�ӂ����ˁB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (93, 15, '���̂��̂��ƂƂ��͂��H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���̂��̂��ƂƂ��͂��H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (94, 15, '����ҋ��Z���Ă�΂���ˁB�Ђт����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u����ҋ��Z���Ă�΂���ˁB�Ђт����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (95, 16, '����񂭂�ɂƂ����߂�ꂽ�B�Ђǂ��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u����񂭂�ɂƂ����߂�ꂽ�B�Ђǂ��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (96, 16, '���S�ƍ߂��Ăނ��������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���S�ƍ߂��Ăނ��������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (97, 16, '���˂��ˁB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���˂��ˁB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (98, 16, '�ڂ������̂��I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ڂ������̂��I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (99, 16, '����낫���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u����낫���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (100, 16, '�ߏ�Ȋ��҂͎��]�̕�ł���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ߏ�Ȋ��҂͎��]�̕�ł���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (101, 16, '�q�����͍���������B�J���C�͐h���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�q�����͍���������B�J���C�͐h���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (102, 16, '�S�n���ȂɁH');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�S�n���ȂɁH�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (103, 17, '���������n�E�`���[�[�[�W���_�[�[�[�I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���������n�E�`���[�[�[�W���_�[�[�[�I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (104, 17, '�j���[�g���m�̎��ʂ��[���łȂ��ƁA�x�[�^����̓d�q�̃G�l���M�[�X�y�N�g���̕ω��ȊO�ɁA�j���[�g���m�U���Ƃ������ۂ������邱�Ƃ��m���Ă��܂��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�j���[�g���m�̎��ʂ��[���łȂ��ƁA�x�[�^����̓d�q�̃G�l���M�[�X�y�N�g���̕ω��ȊO�ɁA�j���[�g���m�U���Ƃ������ۂ������邱�Ƃ��m���Ă��܂��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (105, 17, '�d�ׂ����ʂ���Ƃ��Ė������Ȃ��A�X�s���������B�������ݍ�p���������A�d�q�E��(�~���[)���q�E��(�^�E)���q�Ƒ΂ɂȂ��č�p����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�d�ׂ����ʂ���Ƃ��Ė������Ȃ��A�X�s���������B�������ݍ�p���������A�d�q�E��(�~���[)���q�E��(�^�E)���q�Ƒ΂ɂȂ��č�p����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (106, 17, '�l�Ԃ��Ăǂ��ł����H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�l�Ԃ��Ăǂ��ł����H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (107, 17, '���܂ɂ͔�s�ɑ����Ă݂悤���ȁB�ǂ̂��炢�ő���΂�����H�ł��A����܂艓���ւ͍s���Ȃ�����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���܂ɂ͔�s�ɑ����Ă݂悤���ȁB�ǂ̂��炢�ő���΂�����H�ł��A����܂艓���ւ͍s���Ȃ�����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (108, 17, '�[�сH�����C�H�킽���H ����Ȃ̗[�тɂ��܂��Ă邶���B���łɒ��т����т��s�����Ⴆ��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�[�сH�����C�H�킽���H ����Ȃ̗[�тɂ��܂��Ă邶���B���łɒ��т����т��s�����Ⴆ��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (109, 17, '�����͖����ɂȂ����獡���Ȃ񂾂��A�����͖����ɂȂ�΍������B���Ⴀ�A��������������������������ˁB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����͖����ɂȂ����獡���Ȃ񂾂��A�����͖����ɂȂ�΍������B���Ⴀ�A��������������������������ˁB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (110, 17, '���^�ɔY�ށB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���^�ɔY�ށB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (111, 17, '�r����ꂽ�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�r����ꂽ�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (112, 17, '�ؓ��͎g���Ɖ���񂾂�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ؓ��͎g���Ɖ���񂾂�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (113, 18, '������肪�����Ă�͔̂閧����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u������肪�����Ă�͔̂閧����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (114, 18, '���A�p���c�͂��ĂȂ��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���A�p���c�͂��ĂȂ��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (115, 18, '�ʂ�ہB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ʂ�ہB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (116, 18, '�ޯ�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ޯ�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (117, 18, '�����Ă悵�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����Ă悵�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (118, 18, 'orz�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�uorz�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (119, 18, '��������(߁��)������!!!!!');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u��������(߁��)������!!!!!�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (120, 18, '( �L_�T`)̰�');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u( �L_�T`)̰݁v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (121, 18, '�Q|�P|��');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�Q|�P|���v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (122, 18, '�d�Ԓj���Ă��܂Ȃɂ���Ă�񂾂�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�d�Ԓj���Ă��܂Ȃɂ���Ă�񂾂�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (123, 19, '�Ȃ񂾂�I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�Ȃ񂾂�I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (124, 19, '�^�R���Ă����ȃ^�R���āI�ǂ��݂Ă��C�J����I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�^�R���Ă����ȃ^�R���āI�ǂ��݂Ă��C�J����I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (125, 19, '�N�`�Ƃ񂪂炪���ĂȂɂ������Ă񂾂�I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�N�`�Ƃ񂪂炪���ĂȂɂ������Ă񂾂�I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (126, 19, '���H������H�����낪�ȂɁH��������Ă��܂����������ĊȒP�ɂ͂��܂���Ȃ����I�����낾���Č��Ȃ����I���Ȃ��I���Ȃ����Č��߂��猩�Ȃ��I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���H������H�����낪�ȂɁH��������Ă��܂����������ĊȒP�ɂ͂��܂���Ȃ����I�����낾���Č��Ȃ����I���Ȃ��I���Ȃ����Č��߂��猩�Ȃ��I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (127, 19, '�ΐ��ɋA�肽���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ΐ��ɋA�肽���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (128, 19, '�^�R���[�^�[���ă^�R�̑傫����\�����Ă�񂶂�Ȃ������񂾁I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�^�R���[�^�[���ă^�R�̑傫����\�����Ă�񂶂�Ȃ������񂾁I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (129, 19, '�I�h���[�^�[�͋����s�R�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�I�h���[�^�[�͋����s�R�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (130, 19, '�������');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u��������v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (131, 19, '�����������������I���̊�݂��H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����������������I���̊�݂��H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (132, 19, '���Ȃт��Ⴄ�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���Ȃт��Ⴄ�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (133, 20, '���̋������͊O�ɏo���܂���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���̋������͊O�ɏo���܂���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (134, 20, '�Ă͖X�q���������܂���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�Ă͖X�q���������܂���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (135, 20, '�G���x�[�^�[�ŏ��q�ƈꏏ�ɂȂ����Ƃ��́A�C�𗘂����ĂƂɂ����~��邱�Ƃɂ��Ă��܂��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�G���x�[�^�[�ŏ��q�ƈꏏ�ɂȂ����Ƃ��́A�C�𗘂����ĂƂɂ����~��邱�Ƃɂ��Ă��܂��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (136, 20, '��s�ł͂���܂���B���z�ł��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u��s�ł͂���܂���B���z�ł��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (137, 20, '�����񂪎��ƂɋA��܂����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����񂪎��ƂɋA��܂����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (138, 20, '�q���Ɂu�܂����ĂˁI�v���Č����܂����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�q���Ɂu�܂����ĂˁI�v���Č����܂����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (139, 20, '�����炵�̗ǂ��ȂɈٓ��ɂȂ�܂����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����炵�̗ǂ��ȂɈٓ��ɂȂ�܂����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (140, 20, '�g�у��[���𑗂����̂�2�񂾂��ł��B����͎����ł��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�g�у��[���𑗂����̂�2�񂾂��ł��B����͎����ł��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (141, 20, '�����ɂ͕����Ȃ��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����ɂ͕����Ȃ��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (142, 20, '�Ȃ��������̐Ȃ̃S�~�������ЂÂ��Ă��炦�܂���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�Ȃ��������̐Ȃ̃S�~�������ЂÂ��Ă��炦�܂���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (143, 21, '�o�����X�ւ񂶂�Ȃ��H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�o�����X�ւ񂶂�Ȃ��H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (144, 21, '���������I�I�g�J�T�ɂ����I�I�I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���������I�I�g�J�T�ɂ����I�I�I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (145, 21, '���߂܂���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���߂܂���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (146, 21, '�K���o�����Ă����̂͊ȒP�����ǁA����ꂽ�ق��Ƃ��Ă͖{�S���炻���������t���󂯓����͈̂ĊO�ނ���������ˁB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�K���o�����Ă����̂͊ȒP�����ǁA����ꂽ�ق��Ƃ��Ă͖{�S���炻���������t���󂯓����͈̂ĊO�ނ���������ˁB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (147, 21, '���ނ����ɂ��Ƃ��̂����B���ꂪ�Ȃ�ł��B���Ƃ��Βܐ؂�Ƃ��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���ނ����ɂ��Ƃ��̂����B���ꂪ�Ȃ�ł��B���Ƃ��Βܐ؂�Ƃ��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (148, 21, '�Q��̂ɂ��̗͂������B�̗͂̂Ȃ��l�͐Q��Ȃ��񂾂�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�Q��̂ɂ��̗͂������B�̗͂̂Ȃ��l�͐Q��Ȃ��񂾂�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (149, 21, '���N���͎O���̓����Ă������ǁA�����Ő��������Ȃ��ˁB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���N���͎O���̓����Ă������ǁA�����Ő��������Ȃ��ˁB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (150, 21, '�Ԃ����ł݂����B���̒ꂩ��v��������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�Ԃ����ł݂����B���̒ꂩ��v��������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (151, 21, '�I�V�h���͎��͕s�ς��܂��肾�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�I�V�h���͎��͕s�ς��܂��肾�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (152, 21, '�J�b�R�E���ē�������ȁB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�J�b�R�E���ē�������ȁB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (153, 22, '�A���t�K���h�����������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�A���t�K���h�����������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (154, 22, '���������ł����Ƃ����ĉH�Ȃ񂩐����Ȃ���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���������ł����Ƃ����ĉH�Ȃ񂩐����Ȃ���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (155, 22, '����񂱂͂ǂ�Ȃɍ����Ƃ��납�痎���Ă����ȂȂ��񂾂��āB���킵�Ă݂�H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u����񂱂͂ǂ�Ȃɍ����Ƃ��납�痎���Ă����ȂȂ��񂾂��āB���킵�Ă݂�H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (156, 22, '�ڂ���ɂƂ��āA������������܂����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ڂ���ɂƂ��āA������������܂����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (157, 22, '�����������������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����������������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (158, 22, '����Ƃ����ׂ�H�ڂ��͐l�����D�݁B3�l���炢�y��������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u����Ƃ����ׂ�H�ڂ��͐l�����D�݁B3�l���炢�y��������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (159, 22, '�K�b�����Ə������Ă݂����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�K�b�����Ə������Ă݂����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (160, 22, '�����A�Ȃ񂩓�����o���o���ƐH�ׂ����B�������Ƃ��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����A�Ȃ񂩓�����o���o���ƐH�ׂ����B�������Ƃ��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (161, 22, '�[���ɖڂ��o�߂Ē������邾���킩��Ȃ����Ƃ��ĂȂ��H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�[���ɖڂ��o�߂Ē������邾���킩��Ȃ����Ƃ��ĂȂ��H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (162, 22, '�e���z�[�_�C�H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�e���z�[�_�C�H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (163, 23, '���Ȃ��������I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���Ȃ��������I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (164, 23, '���ׂ�̂����������[�������I���܂��̂��炢�̂����ς��ς��I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���ׂ�̂����������[�������I���܂��̂��炢�̂����ς��ς��I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (165, 23, '�J�~�J�~�J�~�J�~�J�~�J�~�J�~�J�~�J�~�J�~�J�~�I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�J�~�J�~�J�~�J�~�J�~�J�~�J�~�J�~�J�~�J�~�J�~�I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (166, 23, '�����S�͂����Ȃ��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����S�͂����Ȃ��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (167, 23, '�u�͂�Ԃ񂸂����v���Č����Ă���ꂽ�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�u�͂�Ԃ񂸂����v���Č����Ă���ꂽ�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (168, 23, '���[�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���[�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (169, 23, '���̒����āA���Ȃ��ނ��̂��ƁH���Ȃ��ނ������[���[�����́H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���̒����āA���Ȃ��ނ��̂��ƁH���Ȃ��ނ������[���[�����́H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (170, 23, '�ς��ς�����ɂ܂��Ȃ����I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ς��ς�����ɂ܂��Ȃ����I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (171, 23, '�{�C�o���Ό����ňړ��ł��܂���B��������ƂȂ����ǁB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�{�C�o���Ό����ňړ��ł��܂���B��������ƂȂ����ǁB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (172, 23, '���V�L���O�ɂł��B�w���N���X�������I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���V�L���O�ɂł��B�w���N���X�������I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (173, 24, '�ԁ[��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ԁ[��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (174, 24, '������i�@�O�ցO�j�� �ԁ[��');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u������i�@�O�ցO�j�� �ԁ[��v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (175, 24, '���[�_�[�ɂ���Ȃ���B�����ł��邩���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���[�_�[�ɂ���Ȃ���B�����ł��邩���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (176, 24, '�ԂƂ�ڂ̉H������Ă��A�u�����V�ɂ͂Ȃ�Ȃ���ȁB���񂺂񂿂������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ԂƂ�ڂ̉H������Ă��A�u�����V�ɂ͂Ȃ�Ȃ���ȁB���񂺂񂿂������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (177, 24, '���ɂ��܂ɕ������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���ɂ��܂ɕ������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (178, 24, '����܂��������B�Y�΂ŏĂ����T���}�ɂ������񂨂낵�Ƃۂ�|�����炵�āB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u����܂��������B�Y�΂ŏĂ����T���}�ɂ������񂨂낵�Ƃۂ�|�����炵�āB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (179, 24, '�܂������������B���������ƂȂ��B���܂��́H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�܂������������B���������ƂȂ��B���܂��́H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (180, 24, '�g�t���Č͂�Ă�킯����Ȃ��񂾂ˁB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�g�t���Č͂�Ă�킯����Ȃ��񂾂ˁB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (181, 24, '���݂��}�[�N���ĂȂ����t���܂ɓ\���Ă�l���悭����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���݂��}�[�N���ĂȂ����t���܂ɓ\���Ă�l���悭����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (182, 24, '�u�q�����̂��Ă܂��v�X�e�b�J�[�̃p���f�B�[���悭����B���Ȃ�o�J���ۂ��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�u�q�����̂��Ă܂��v�X�e�b�J�[�̃p���f�B�[���悭����B���Ȃ�o�J���ۂ��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (183, 25, '���������E�Ɂ[�E����[�E���[�E�Ɂ[�E�ɂ��E����[�E���[�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���������E�Ɂ[�E����[�E���[�E�Ɂ[�E�ɂ��E����[�E���[�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (184, 25, '�����^���ŃP�K�����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����^���ŃP�K�����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (185, 25, '�p���`�ƃp���c���Ď��Ă�B�Ȃ�ƂȂ��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�p���`�ƃp���c���Ď��Ă�B�Ȃ�ƂȂ��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (186, 25, '�ŋ߂̖���̃L�������ċ������B�����ȒP�ɐ΂͊���Ȃ��Ǝv���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ŋ߂̖���̃L�������ċ������B�����ȒP�ɐ΂͊���Ȃ��Ǝv���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (187, 25, '�Ђ��ɐ������܂����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�Ђ��ɐ������܂����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (188, 25, '�T�̂�����w�����ďC�s������J���n���g�ł邩�ȁH');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�T�̂�����w�����ďC�s������J���n���g�ł邩�ȁH�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (189, 25, '�P���V���E�Ƃʂ������搶�ǂ������������ȁB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�P���V���E�Ƃʂ������搶�ǂ������������ȁB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (190, 25, '���݂₰�ɖؓ������Ă����B������񎩕��p�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���݂₰�ɖؓ������Ă����B������񎩕��p�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (191, 25, '�X�p�Q�e�B�[�̓I���[�u�I�C���Ɖ������傤�����ł�������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�X�p�Q�e�B�[�̓I���[�u�I�C���Ɖ������傤�����ł�������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (192, 25, '���Ɩ�؂̓o�����X�ǂ��H�ׂ悤�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���Ɩ�؂̓o�����X�ǂ��H�ׂ悤�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (193, 26, '�����Ӂ`��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����Ӂ`��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (194, 26, '�ӂ��ɍl���Ď�_����蒆���̂ق������ɂ₳�����Ǝv���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ӂ��ɍl���Ď�_����蒆���̂ق������ɂ₳�����Ǝv���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (195, 26, '�����ŔN���o����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����ŔN���o����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (196, 26, '1�~�������̂�1000�������Ƃ��A10000�~�̂��̂�9000�~�Ŕ����w�͂������ق��������Ǝv���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u1�~�������̂�1000�������Ƃ��A10000�~�̂��̂�9000�~�Ŕ����w�͂������ق��������Ǝv���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (197, 26, '�����̒a�����͊�΂Ȃ��̂ɁA���l�̒a�����͏j��������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����̒a�����͊�΂Ȃ��̂ɁA���l�̒a�����͏j��������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (198, 26, '�ʕ��̑��݂���3�i���̂ق����C�ɂȂ�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ʕ��̑��݂���3�i���̂ق����C�ɂȂ�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (199, 26, '�{���͑吷�肪�H�ׂ����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�{���͑吷�肪�H�ׂ����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (200, 26, '�����̔��@�ŊʃR�[�q�[�������Ȃ��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����̔��@�ŊʃR�[�q�[�������Ȃ��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (201, 26, '����܂��񂪌��܂݂�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u����܂��񂪌��܂݂�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (202, 26, '��s����Ƃ������_�o�����ǂƂ��T�Ƃ��f�f�����Ƃ�����Ɗ������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u��s����Ƃ������_�o�����ǂƂ��T�Ƃ��f�f�����Ƃ�����Ɗ������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (203, 27, '����Ȃ����ȋC������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u����Ȃ����ȋC������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (204, 27, '�Ȃ�ő������Ȃ񂾂낤�B����~���������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�Ȃ�ő������Ȃ񂾂낤�B����~���������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (205, 27, '��Ȃ�ď���ł�����I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u��Ȃ�ď���ł�����I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (206, 27, '�_���v���{�Ɏ��Ă���Č���ꂽ�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�_���v���{�Ɏ��Ă���Č���ꂽ�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (207, 27, '�n���o�[�K�[���ׂ����B�r�b�O�}�b�N�������[�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�n���o�[�K�[���ׂ����B�r�b�O�}�b�N�������[�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (208, 27, '�}�N�h�i���h�̃s�N���X���Ă������Ǝv���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�}�N�h�i���h�̃s�N���X���Ă������Ǝv���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (209, 27, '��߂��t���C�h�|�e�g�ł��ւ����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u��߂��t���C�h�|�e�g�ł��ւ����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (210, 27, '�}���l�[�Y���ד��Ƃ������c���炢�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�}���l�[�Y���ד��Ƃ������c���炢�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (211, 27, '�ᓹ���|���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ᓹ���|���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (212, 27, '�]�񂾂�N�����Ȃ����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�]�񂾂�N�����Ȃ����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (213, 28, '����͂���I����͂��ʂ��������I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u����͂���I����͂��ʂ��������I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (214, 28, '�u���Ȃ�ď���ł��v���Č���ꂿ�Ⴂ�܂������Ȃɂ��H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�u���Ȃ�ď���ł��v���Č���ꂿ�Ⴂ�܂������Ȃɂ��H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (215, 28, '�]�V��������ꂽ�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�]�V��������ꂽ�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (216, 28, '�΂����炿����ƃ��K���q�ӂ�������������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�΂����炿����ƃ��K���q�ӂ�������������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (217, 28, '�r�[���͌����Ȃ���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�r�[���͌����Ȃ���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (218, 28, '�X���b�K�[�Ȃ�]�T�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�X���b�K�[�Ȃ�]�T�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (219, 28, '�R�A�u�[�X�^�[�͉f��ŃI���W�i�����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�R�A�u�[�X�^�[�͉f��ŃI���W�i�����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (220, 28, '�F�������Ă��ꂽ��K���}�͎��񂾁B ���̂��I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�F�������Ă��ꂽ��K���}�͎��񂾁B ���̂��I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (221, 28, '�U�r�Ƃ̉h���I���̉��̃v���C�h�I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�U�r�Ƃ̉h���I���̉��̃v���C�h�I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (222, 28, '���|�I����Ȃ����I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���|�I����Ȃ����I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (223, 29, '���񂺂񈬗͂��Ȃ��B�ʂ�����݂������グ���Ȃ��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���񂺂񈬗͂��Ȃ��B�ʂ�����݂������グ���Ȃ��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (224, 29, '�u�����d�����̂������Ȃ��v���āA���ł��т����񂾂�����_�����Ǝv���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�u�����d�����̂������Ȃ��v���āA���ł��т����񂾂�����_�����Ǝv���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (225, 29, '����񂯂�ŕ����������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u����񂯂�ŕ����������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (226, 29, '�J�j�ɂ͏��Ă����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�J�j�ɂ͏��Ă����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (227, 29, '�I�]���z�[�����ӂ����ɍs���Ă����B���Ȃ�Č�����Ȃ�������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�I�]���z�[�����ӂ����ɍs���Ă����B���Ȃ�Č�����Ȃ�������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (228, 29, '�j���[�g���m���ĂȂɁH');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�j���[�g���m���ĂȂɁH�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (229, 29, '�E�ƍ����悭�ԈႦ�܂��B����Ȃɂ͂����Ȃ������B�J�[�i�r�����āB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�E�ƍ����悭�ԈႦ�܂��B����Ȃɂ͂����Ȃ������B�J�[�i�r�����āB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (230, 29, '������������炨���܂��Ȏ�������΁A���������Ȃ���͂��܂�Ȃ���������B�ł��A���Ԃ񂪉����������Ƃ��Ă�̂����āA�悭�킩��Ȃ���ˁB��ɂȂ��Ă���킩�����肷�鎞�����邯�ǂ��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u������������炨���܂��Ȏ�������΁A���������Ȃ���͂��܂�Ȃ���������B�ł��A���Ԃ񂪉����������Ƃ��Ă�̂����āA�悭�킩��Ȃ���ˁB��ɂȂ��Ă���킩�����肷�鎞�����邯�ǂ��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (231, 29, '�Ȃ��NTT�̓J�[�h�����ł��Ȃ��񂾂낤�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�Ȃ��NTT�̓J�[�h�����ł��Ȃ��񂾂낤�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (232, 29, '�������܁A���Ȃ�F���H���݂̂����Ȃ��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�������܁A���Ȃ�F���H���݂̂����Ȃ��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (233, 30, '�T�C�R�~���t������G�����X�ɂȂꂽ�����H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�T�C�R�~���t������G�����X�ɂȂꂽ�����H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (234, 30, '�����@�ڂ����������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����@�ڂ����������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (235, 30, '���̃X�s�[�h���@�悯���邩�H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���̃X�s�[�h���@�悯���邩�H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (236, 30, '�t���A�~�T�C���̒e���𒣂���Ă����̂͂����������ɂ��̂�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�t���A�~�T�C���̒e���𒣂���Ă����̂͂����������ɂ��̂�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (237, 30, '��H�t�������t�������B���A����A�������܂����Ȃ�����x�̃V���b�N�ŋC�₵�Ă���͂����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u��H�t�������t�������B���A����A�������܂����Ȃ�����x�̃V���b�N�ŋC�₵�Ă���͂����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (238, 30, '�J�j���y�Ƃ܂�����ꂽ�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�J�j���y�Ƃ܂�����ꂽ�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (239, 30, '���̗ʎY�^���r���A�[�}�[���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���̗ʎY�^���r���A�[�}�[���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (240, 30, '���ʂɍl�����烂�r���X�[�c��胂�r���A�[�}�[�̂ق�����ɏo�Ă����ˁB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���ʂɍl�����烂�r���X�[�c��胂�r���A�[�}�[�̂ق�����ɏo�Ă����ˁB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (241, 30, '�U�N�����̃f�U�C���͂��������Ȃ���ˁB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�U�N�����̃f�U�C���͂��������Ȃ���ˁB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (242, 30, '���Ȃ�ď���ł�����I���Ă��̂Ƃ������Ă��ǂ������ˁB');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���Ȃ�ď���ł�����I���Ă��̂Ƃ������Ă��ǂ������ˁB�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (243, 31, '�ɂ�`��`�ɂ�`��`�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�ɂ�`��`�ɂ�`��`�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (244, 31, '�����Ƃ����Ƃ����h��͂���؂����I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����Ƃ����Ƃ����h��͂���؂����I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (245, 31, '�񐶒��������Ă邱�Ƃ�����̂ŁA���������K�����􂨂��I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�񐶒��������Ă邱�Ƃ�����̂ŁA���������K�����􂨂��I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (246, 31, '�������ł��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�������ł��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (247, 31, '���������ł��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���������ł��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (248, 31, '�Ăѕ��𓝈ꂵ�Ă��������I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�Ăѕ��𓝈ꂵ�Ă��������I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (249, 31, '�c�m�͂킩�邯�ǃ������Ăǂ����낤�H');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�c�m�͂킩�邯�ǃ������Ăǂ����낤�H�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (250, 31, '�E�����ƍ����������܂��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�E�����ƍ����������܂��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (251, 31, '�������ĐH�����Ⴂ�܂��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�������ĐH�����Ⴂ�܂��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (252, 31, '�̂�؂��Ă��w�b�`�������B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�̂�؂��Ă��w�b�`�������B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (253, 32, '�Ȃɂ��Ȃ񂾂��킩��܂���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�Ȃɂ��Ȃ񂾂��킩��܂���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (254, 32, '�񑩂��Ȃ���I');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�񑩂��Ȃ���I�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (255, 32, '�����ȂǂȂ��B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����ȂǂȂ��B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (256, 32, '�V�т����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�V�т����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (257, 32, '���c���E�i�M�̖ڂ͕��ʂ�2�����Ȃ���B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���c���E�i�M�̖ڂ͕��ʂ�2�����Ȃ���B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (258, 32, '�h��Y�ꂽ�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�h��Y�ꂽ�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (259, 32, '�����͒�����邾�����B�ǂ���܂������{����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�����͒�����邾�����B�ǂ���܂������{����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (260, 32, '�~�V���̔����҂̓~�V���𔭖��������Ƃŕ��̎d���ĉ��ɏP��ꂽ�B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u�~�V���̔����҂̓~�V���𔭖��������Ƃŕ��̎d���ĉ��ɏP��ꂽ�B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (261, 32, '���g�D�f�X�g�����̏Z�����킩�����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u���g�D�f�X�g�����̏Z�����킩�����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (262, 32, '����Ƃ񂶂�̂����B');
		if ($sth->execute(@bind)) {
			push(@msgs, '�u����Ƃ񂶂�̂����B�v�쐬����');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}



	$dbh->disconnect
		or die($DBI::err . ':' . $DBI::errstr);
	
	push(@msgs, '�I��');
}
