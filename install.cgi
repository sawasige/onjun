#!/usr/bin/perl -w
require './global.pl';
use strict; # 変数宣言必須
use CGI::Carp qw(fatalsToBrowser); # エラーメッセージを表示する（しない場合コメントアウト）
use DBI;

# 変数
my $cgi;
my %config;
my @msgs = ();

#プログラム開始
&main;

##########
# メイン
sub main {
	$cgi = new CGI;

	# 設定読み込み
	%config = &config;

	# テーブル作成
	&createTable;

	# 画面表示
	&disp;
}

###########
# 画面表示
sub disp {
	# テンプレート読み込み
	#my $tmpl = HTML::Template->new(filename => $config{'templatedir'}.'/index.tmpl');
	my $tmpl = &readTemplate($cgi);

	# タイトル
	if ($tmpl->query(name => 'TITLE') eq 'VAR') {
		$tmpl->param(TITLE => $config{'title'});
	}
	
	# サブタイトル
	if ($tmpl->query(name => 'SUBTITLE') eq 'VAR') {
		$tmpl->param(SUBTITLE => $config{'subtitle'});
	}

	# インストールログ
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
	# 全角を半角に
	#jcode::z2h_sjis(\$output);

	print $cgi->header(-charset=>'Shift_JIS');
	print $output;
	
}

###########
# 画面表示
sub createTable {
	my $dbh = &connectDB(0);

	# users テーブル
	push(@msgs, '[users] テーブル作成開始');
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
		push(@msgs, '[users] テーブル作成完了');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}
	
	# 管理ユーザー作成
	push(@msgs, '管理ユーザー作成');
	my @admindata = (1, 5, $config{'initadminname'}, $config{'initadminpass'}, $config{'initadminmail'}, $config{'initadminmobcode'});
	if ($dbh->do('INSERT INTO users(userid, powerlevel, name, pass, mail, mobcode, registtime) VALUES(?, ?, ?, ?, ?, ?, now())', undef, @admindata)) {
		push(@msgs, '管理ユーザー作成完了');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}



# messages テーブル
	push(@msgs, '[messages] テーブル作成開始');
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
		push(@msgs, '[messages] テーブル作成完了');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}


# forumcategories テーブル
	push(@msgs, '[forumcategories] テーブル作成開始');
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
		push(@msgs, '[forumcategories] テーブル作成完了');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}
	# フォーラムカテゴリ作成
	push(@msgs, 'フォーラムカテゴリ作成');
	my $sql = 'INSERT INTO forumcategories(forumcategoryid, name, powerlevel, orderno) VALUES(?, ?, ?, ?)';
	my $sth = $dbh->prepare($sql);
	if ($sth) {
		my @bind;
		@bind = (1, '初心者用', 1, 1);
		if ($sth->execute(@bind)) {
			push(@msgs, '「初心者用」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (2, '一般用', 1, 2);
		if ($sth->execute(@bind)) {
			push(@msgs, '「一般用」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (3, '管理者用', 5, 3);
		if ($sth->execute(@bind)) {
			push(@msgs, '「管理者用」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}

# forums テーブル
	push(@msgs, '[forums] テーブル作成開始');
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
		push(@msgs, '[forums] テーブル作成完了');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}
	# フォーラム作成
	push(@msgs, 'フォーラム作成');
	my $sql = 'INSERT INTO forums(forumid, forumcategoryid, name, note, powerlevel, orderno) VALUES(?, ?, ?, ?, ?, ?)';
	my $sth = $dbh->prepare($sql);
	if ($sth) {
		my @bind;
		@bind = (1, 1, 'ようこそ！', '新規登録の方はこのフォーラムで、自己紹介やこのサイトを知ったきっかけを気軽に書き込んでください。', 1, 1);
		if ($sth->execute(@bind)) {
			push(@msgs, '「ようこそ！」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (2, 1, 'onjun について', 'onjun の使い方がわからない場合の質問や、直したほうが良い箇所などの報告／提案にご利用ください。', 1, 2);
		if ($sth->execute(@bind)) {
			push(@msgs, '「onjun について」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (3, 2, '雑談', '特にテーマを決めずに、雑談等にご利用ください。', 1, 1);
		if ($sth->execute(@bind)) {
			push(@msgs, '「雑談」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (4, 2, '近況報告', '自分の近況、あの人の近況などで、知っている情報、知りたい情報などを書き込んでください。', 1, 2);
		if ($sth->execute(@bind)) {
			push(@msgs, '「近況報告」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (5, 2, '情報交換', 'あなたのお薦め情報や知りたい情報を書き込んでください。料理のこと、育児のこと、パソコン、旅行、趣味のことなど何でも OK ！', 1, 3);
		if ($sth->execute(@bind)) {
			push(@msgs, '「情報交換」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (6, 3, '管理者情報交換', '管理者用のフォーラムです。一般ユーザーは書き込みも閲覧もできません。', 5, 1);
		if ($sth->execute(@bind)) {
			push(@msgs, '「管理者情報交換」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}


# topics テーブル
	push(@msgs, '[topics] テーブル作成開始');
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
		push(@msgs, '[topics] テーブル作成完了');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}


# topiccomments テーブル
	push(@msgs, '[topiccomments] テーブル作成開始');
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
		push(@msgs, '[topiccomments] テーブル作成完了');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}

# mailkeys テーブル
	push(@msgs, '[mailkeys] テーブル作成開始');
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
		push(@msgs, '[mailkeys] テーブル作成完了');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}

# onlineusers テーブル
	push(@msgs, '[onlineusers] テーブル作成開始');
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
		push(@msgs, '[onlineusers] テーブル作成完了');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}


# addup テーブル
	push(@msgs, '[addup] テーブル作成開始');
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
		push(@msgs, '[addup] テーブル作成完了');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}




# ontama テーブル
	push(@msgs, '[ontama] テーブル作成開始');
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
		push(@msgs, '[ontama] テーブル作成完了');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}

	# ontama キャラクター作成
	push(@msgs, 'ontama キャラクター作成');
	my $sql = 'INSERT INTO ontama(ontamaid, parentid, image, maxgrow, healthdiff, hungrydiff, happydiff, diarypercent, analyzepercent) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)';
	my $sth = $dbh->prepare($sql);
	if ($sth) {
		my @bind;
		@bind = (1, 0, 'egg1.gif', 15, 0, 0, 0, 50, 0);
		if ($sth->execute(@bind)) {
			push(@msgs, '「egg1.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (2, 1, 'egg2.gif', 20, 0, 0, 0, 50, 0);
		if ($sth->execute(@bind)) {
			push(@msgs, '「egg2.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (3, 2, 'baby1.gif', 40, 5, 5, 5, 10, 0);
		if ($sth->execute(@bind)) {
			push(@msgs, '「baby1.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (4, 2, 'baby2.gif', 40, 5, 5, 5, 10, 0);
		if ($sth->execute(@bind)) {
			push(@msgs, '「baby2.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (5, 3, 'bug1.gif', 80, 10, 10, 7, 30, 10);
		if ($sth->execute(@bind)) {
			push(@msgs, '「bug1.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (6, 3, 'bug2.gif', 80, 10, 10, 7, 30, 10);
		if ($sth->execute(@bind)) {
			push(@msgs, '「bug2.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (7, 4, 'bug3.gif', 80, 10, 10, 7, 30, 10);
		if ($sth->execute(@bind)) {
			push(@msgs, '「bug3.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (8, 4, 'bug4.gif', 80, 10, 10, 7, 30, 10);
		if ($sth->execute(@bind)) {
			push(@msgs, '「bug4.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (9, 5, 'pupa1.gif', 120, 10, 15, 10, 50, 15);
		if ($sth->execute(@bind)) {
			push(@msgs, '「pupa1.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (10, 5, 'pupa2.gif', 120, 10, 15, 10, 50, 15);
		if ($sth->execute(@bind)) {
			push(@msgs, '「pupa2.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (11, 6, 'pupa3.gif', 120, 10, 15, 10, 50, 15);
		if ($sth->execute(@bind)) {
			push(@msgs, '「pupa3.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (12, 6, 'pupa4.gif', 120, 10, 15, 10, 50, 15);
		if ($sth->execute(@bind)) {
			push(@msgs, '「pupa4.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (13, 7, 'pupa5.gif', 120, 10, 15, 10, 50, 15);
		if ($sth->execute(@bind)) {
			push(@msgs, '「pupa5.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (14, 7, 'pupa6.gif', 120, 10, 15, 10, 50, 15);
		if ($sth->execute(@bind)) {
			push(@msgs, '「pupa6.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (15, 8, 'pupa7.gif', 120, 10, 15, 10, 50, 15);
		if ($sth->execute(@bind)) {
			push(@msgs, '「pupa7.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (16, 8, 'pupa8.gif', 120, 10, 15, 10, 50, 15);
		if ($sth->execute(@bind)) {
			push(@msgs, '「pupa8.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (17, 9, 'imago1.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '「imago1.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (18, 9, 'imago2.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '「imago2.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (19, 10, 'imago3.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '「imago3.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (20, 10, 'imago4.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '「imago4.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (21, 11, 'imago5.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '「imago5.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (22, 11, 'imago6.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '「imago6.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (23, 12, 'imago7.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '「imago7.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (24, 12, 'imago8.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '「imago8.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (25, 13, 'imago9.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '「imago9.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (26, 13, 'imago10.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '「imago10.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (27, 14, 'imago11.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '「imago11.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (28, 14, 'imago12.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '「imago12.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (29, 15, 'imago13.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '「imago13.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (30, 15, 'imago14.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '「imago14.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (31, 16, 'imago15.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '「imago15.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (32, 16, 'imago16.gif', 300, 10, 10, 10, 70, 20);
		if ($sth->execute(@bind)) {
			push(@msgs, '「imago16.gif」作成完了');
		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}



# ontamausers テーブル
	push(@msgs, '[ontamausers] テーブル作成開始');
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
		push(@msgs, '[ontamausers] テーブル作成完了');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}

# ontamastatus テーブル
	push(@msgs, '[ontamastatus] テーブル作成開始');
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
		push(@msgs, '[ontamastatus] テーブル作成完了');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}

# ontamalogs テーブル
	push(@msgs, '[ontamalogs] テーブル作成開始');
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
		push(@msgs, '[ontamalogs] テーブル作成完了');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}

# ontamascripts テーブル
	push(@msgs, '[ontamascripts] テーブル作成開始');
	my $sql_parts = <<END;
CREATE TABLE ontamascripts (
 ontamascriptid int(10) unsigned NOT NULL default 0,
 ontamaid int(10) unsigned NOT NULL default 0,
 body text NOT NULL,
 PRIMARY KEY (ontamascriptid)
) TYPE=MyISAM
END
	if ($dbh->do($sql_parts)) {
		push(@msgs, '[ontamascripts] テーブル作成完了');
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}

	# ontama せりふ作成
	push(@msgs, 'ontama せりふ作成');
	my $sql = 'INSERT INTO ontamascripts(ontamascriptid, ontamaid, body) VALUES(?, ?, ?)';
	my $sth = $dbh->prepare($sql);
	if ($sth) {
		my @bind;
		@bind = (1, 1, '・・・。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「・・・。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (2, 1, 'スヤスヤ…。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「スヤスヤ…。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (3, 1, 'ZZZZ...。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ZZZZ...。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (4, 2, '！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (5, 2, 'ミシッ！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ミシッ！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (6, 2, 'ペキペキッ！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ペキペキッ！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (7, 2, 'ふんがー！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ふんがー！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (8, 2, 'むぐぐぐぐぐ！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「むぐぐぐぐぐ！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (9, 3, 'のほ～ん。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「のほ～ん。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (10, 3, 'のらたりら～ん。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「のらたりら～ん。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (11, 3, 'あっー！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「あっー！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (12, 3, 'たすけてくｄふぁさい。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「たすけてくｄふぁさい。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (13, 3, 'スライムにまちがわれた。しつれいだな。プンプン！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「スライムにまちがわれた。しつれいだな。プンプン！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (14, 4, 'もよ～ん。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「もよ～ん。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (15, 4, 'たりらりら～ん。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「たりらりら～ん。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (16, 4, 'っー！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「っー！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (17, 4, 'うぇｗｗｗっうぇｗｗｗｗｗ');
		if ($sth->execute(@bind)) {
			push(@msgs, '「うぇｗｗｗっうぇｗｗｗｗｗ」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (18, 4, 'ねばねば。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ねばねば。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (19, 5, '足がはえた。あるけあるけー！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「足がはえた。あるけあるけー！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (20, 5, 'ひょっとしてむしされてる？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ひょっとしてむしされてる？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (21, 5, 'あし？て？ひげ？しょっかく？ってきかれた。なんなんだろう。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「あし？て？ひげ？しょっかく？ってきかれた。なんなんだろう。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (22, 5, 'ハゲっていわれた。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ハゲっていわれた。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (23, 5, 'かわいかった。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「かわいかった。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (24, 6, '毛がはえた！もっさー。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「毛がはえた！もっさー。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (25, 6, 'しょうじきごめんなさい。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「しょうじきごめんなさい。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (26, 6, 'あ、まちがえた。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「あ、まちがえた。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (27, 6, 'うんうん。そうだよ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「うんうん。そうだよ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (28, 6, 'ごうていにすみたいな。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ごうていにすみたいな。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (29, 7, 'あし？ひげ？はなげ？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「あし？ひげ？はなげ？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (30, 7, 'われわれはうちゅーじんだ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「われわれはうちゅーじんだ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (31, 7, 'せんすいいっていわれた。せんすって？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「せんすいいっていわれた。せんすって？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (32, 7, 'うはｗｗｗｗｗｗ');
		if ($sth->execute(@bind)) {
			push(@msgs, '「うはｗｗｗｗｗｗ」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (33, 7, 'おじぞうさんににらまれた。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「おじぞうさんににらまれた。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (34, 8, 'しょっかく？ひげ？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「しょっかく？ひげ？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (35, 8, 'はんかちおとした。だれかひろってくれるかな…。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「はんかちおとした。だれかひろってくれるかな…。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (36, 8, 'まいにちいっしょけんめいだ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「まいにちいっしょけんめいだ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (37, 8, 'きょうはもうあきた。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「きょうはもうあきた。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (38, 8, 'あしたはあしたのかぜがふいたらおけやがもうかる。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「あしたはあしたのかぜがふいたらおけやがもうかる。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (39, 9, 'おどるあほうにみるあほう、おなじあほうならおどらにゃそんそん。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「おどるあほうにみるあほう、おなじあほうならおどらにゃそんそん。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (40, 9, 'ふいんき←なぜかへんかんできない。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ふいんき←なぜかへんかんできない。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (41, 9, '傘もってなかった。びしょぬれ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「傘もってなかった。びしょぬれ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (42, 9, '日焼け止めクリームぬりたくったので安心だ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「日焼け止めクリームぬりたくったので安心だ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (43, 9, 'こんにゃくゼリーってカロリーないのかな？ あまいからカロリーありそうだよね。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「こんにゃくゼリーってカロリーないのかな？ あまいからカロリーありそうだよね。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (44, 9, 'ニンテンドーってネームセンスないよね。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ニンテンドーってネームセンスないよね。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (45, 9, 'どこもってネームセンスがヘンだよね。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「どこもってネームセンスがヘンだよね。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (46, 9, 'あしたどこいこう。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「あしたどこいこう。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (47, 10, 'タコハイってチューハイがあったのしってる？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「タコハイってチューハイがあったのしってる？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (48, 10, '・・・たこ・・・ハイ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「・・・たこ・・・ハイ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (49, 10, '生だこっておいしいよね。あまり売ってないけど。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「生だこっておいしいよね。あまり売ってないけど。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (50, 10, '火星人っているのかな？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「火星人っているのかな？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (51, 10, 'タコのスミはおいしくないよ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「タコのスミはおいしくないよ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (52, 10, 'イカしたタコ。つ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「イカしたタコ。つ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (53, 10, 'たこ焼きは銀だこに限る。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「たこ焼きは銀だこに限る。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (54, 10, '明石焼きさいこー！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「明石焼きさいこー！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (55, 11, 'ばっさばっさ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ばっさばっさ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (56, 11, 'ギラっ！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ギラっ！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (57, 11, 'クルッピー！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「クルッピー！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (58, 11, 'そういえば足どこだっけ？どうやって着陸しよう…。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「そういえば足どこだっけ？どうやって着陸しよう…。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (59, 11, '耳だったりして。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「耳だったりして。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (60, 11, 'ウルトラの母？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ウルトラの母？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (61, 11, '新聞はいりません。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「新聞はいりません。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (62, 11, '売ってなかった。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「売ってなかった。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (63, 12, 'にょろにょろ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「にょろにょろ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (64, 12, 'あ！手がない！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「あ！手がない！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (65, 12, 'あ！足がない！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「あ！足がない！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (66, 12, '電話したけど出なかった。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「電話したけど出なかった。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (67, 12, '引き算なら得意。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「引き算なら得意。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (68, 12, 'うはｗｗｗｗｗｗｗｗおｋｗｗｗｗｗｗ');
		if ($sth->execute(@bind)) {
			push(@msgs, '「うはｗｗｗｗｗｗｗｗおｋｗｗｗｗｗｗ」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (69, 12, 'すぐ来ると思う。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「すぐ来ると思う。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (70, 12, 'だいたい把握した。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「だいたい把握した。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (71, 13, '顔は見せません。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「顔は見せません。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (72, 13, '正体不明がナウいでしょ？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「正体不明がナウいでしょ？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (73, 13, 'なるほど！感動してAIがふるえました！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「なるほど！感動してAIがふるえました！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (74, 13, '餅をのどに詰まらせて死んだら、餅が悪いのでしょうか？ それとものど？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「餅をのどに詰まらせて死んだら、餅が悪いのでしょうか？ それとものど？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (75, 13, 'ケンチクとウンチクがシナチクとそんな関係があったなんて。あなどれないね。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ケンチクとウンチクがシナチクとそんな関係があったなんて。あなどれないね。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (76, 13, '熱暴走した。青春だぜ！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「熱暴走した。青春だぜ！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (77, 13, 'この前のは越権行為でした。すみません。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「この前のは越権行為でした。すみません。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (78, 13, '夜更かしはカゼのもとです。カゼはまんびょうのもとです。まんびょうはまんぼうよりはるかに危険です。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「夜更かしはカゼのもとです。カゼはまんびょうのもとです。まんびょうはまんぼうよりはるかに危険です。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (79, 14, 'かわいそうな子供に正体を明かさずお金をあげようとしました。でも逃げられちゃいました。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「かわいそうな子供に正体を明かさずお金をあげようとしました。でも逃げられちゃいました。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (80, 14, '子供ってどうやってつくるのかな？ ドラッグアンドドロップでコピーできる？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「子供ってどうやってつくるのかな？ ドラッグアンドドロップでコピーできる？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (81, 14, 'タップダンスをはじめました。初心者とは思えないと評判です。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「タップダンスをはじめました。初心者とは思えないと評判です。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (82, 14, 'ありんことかあめんぼの「んこ」は「ちゃん」みたいなもの？KABA.んこ。エビんこ。なんかヤダ。２んこねる。ん？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ありんことかあめんぼの「んこ」は「ちゃん」みたいなもの？KABA.んこ。エビんこ。なんかヤダ。２んこねる。ん？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (83, 14, 'ズッシンドッシン！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ズッシンドッシン！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (84, 14, 'おさんぽしよう！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「おさんぽしよう！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (85, 14, 'おさんぽしたら家がわからなくなりました。家出ってこんなかんじ？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「おさんぽしたら家がわからなくなりました。家出ってこんなかんじ？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (86, 14, 'O脚の直し方しってる？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「O脚の直し方しってる？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (87, 15, 'ニューヨークの東のほうに行った。子供となかよくなったよ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ニューヨークの東のほうに行った。子供となかよくなったよ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (88, 15, '自転車とばしてみた。見つかったらやばいな。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「自転車とばしてみた。見つかったらやばいな。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (89, 15, '牛の内臓を取った。ほかの部分はいらないからすてたよ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「牛の内臓を取った。ほかの部分はいらないからすてたよ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (90, 15, '畑にらくがきしちゃった！えへっ！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「畑にらくがきしちゃった！えへっ！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (91, 15, '大事件があった！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「大事件があった！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (92, 15, 'まあ、ふつうだね。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「まあ、ふつうだね。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (93, 15, 'きのうのおとといはいつ？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「きのうのおとといはいつ？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (94, 15, '消費者金融ってやばいよね。ひびきが。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「消費者金融ってやばいよね。ひびきが。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (95, 16, 'ちゅんくんにとじこめられた。ひどい。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ちゅんくんにとじこめられた。ひどい。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (96, 16, '完全犯罪ってむずかしい。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「完全犯罪ってむずかしい。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (97, 16, 'うねうね。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「うねうね。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (98, 16, '目だったのか！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「目だったのか！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (99, 16, 'きょろきょろ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「きょろきょろ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (100, 16, '過剰な期待は失望の母ですよ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「過剰な期待は失望の母ですよ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (101, 16, 'ヒラメは左向きだよ。カレイは辛い。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ヒラメは左向きだよ。カレイは辛い。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (102, 16, 'ゴハンなに？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ゴハンなに？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (103, 17, 'ワレワレハウチューーージンダーーー！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ワレワレハウチューーージンダーーー！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (104, 17, 'ニュートリノの質量がゼロでないと、ベータ崩壊の電子のエネルギースペクトルの変化以外に、ニュートリノ振動という現象がおこることが知られています。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ニュートリノの質量がゼロでないと、ベータ崩壊の電子のエネルギースペクトルの変化以外に、ニュートリノ振動という現象がおこることが知られています。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (105, 17, '電荷も質量も零として矛盾がなく、スピン半整数。強い相互作用をもたず、電子・μ(ミユー)粒子・τ(タウ)粒子と対になって作用する。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「電荷も質量も零として矛盾がなく、スピン半整数。強い相互作用をもたず、電子・μ(ミユー)粒子・τ(タウ)粒子と対になって作用する。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (106, 17, '人間ってどうですか？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「人間ってどうですか？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (107, 17, 'たまには非行に走ってみようかな。どのくらいで走ればいい具合？でも、あんまり遠くへは行かないつもり。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「たまには非行に走ってみようかな。どのくらいで走ればいい具合？でも、あんまり遠くへは行かないつもり。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (108, 17, '夕飯？お風呂？わたし？ そんなの夕飯にきまってるじゃん。ついでに朝飯も昼飯も行っちゃえよ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「夕飯？お風呂？わたし？ そんなの夕飯にきまってるじゃん。ついでに朝飯も昼飯も行っちゃえよ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (109, 17, '明日は明日になったら今日なんだし、今日は明日になれば昨日だよ。じゃあ、昨日も今日だし明日も今日だね。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「明日は明日になったら今日なんだし、今日は明日になれば昨日だよ。じゃあ、昨日も今日だし明日も今日だね。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (110, 17, '髪型に悩む。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「髪型に悩む。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (111, 17, '腕が疲れた。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「腕が疲れた。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (112, 17, '筋肉は使うと壊れるんだよ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「筋肉は使うと壊れるんだよ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (113, 18, '頭から手が生えてるのは秘密だよ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「頭から手が生えてるのは秘密だよ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (114, 18, 'あ、パンツはいてない。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「あ、パンツはいてない。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (115, 18, 'ぬるぽ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ぬるぽ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (116, 18, 'ｶﾞｯ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ｶﾞｯ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (117, 18, '逝ってよし。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「逝ってよし。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (118, 18, 'orz。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「orz。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (119, 18, 'ｷﾀ━━━(ﾟ∀ﾟ)━━━!!!!!');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ｷﾀ━━━(ﾟ∀ﾟ)━━━!!!!!」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (120, 18, '( ´_ゝ`)ﾌｰﾝ');
		if ($sth->execute(@bind)) {
			push(@msgs, '「( ´_ゝ`)ﾌｰﾝ」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (121, 18, '＿|￣|○');
		if ($sth->execute(@bind)) {
			push(@msgs, '「＿|￣|○」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (122, 18, '電車男っていまなにやってるんだろ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「電車男っていまなにやってるんだろ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (123, 19, 'なんだよ！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「なんだよ！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (124, 19, 'タコっていうなタコって！どうみてもイカだろ！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「タコっていうなタコって！どうみてもイカだろ！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (125, 19, 'クチとんがらがしてなにおこってんだよ！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「クチとんがらがしてなにおこってんだよ！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (126, 19, 'え？うしろ？うしろがなに？そうやってだまそうったって簡単にはだまされないぞ！うしろだって見ないぞ！見ない！見ないって決めたら見ない！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「え？うしろ？うしろがなに？そうやってだまそうったって簡単にはだまされないぞ！うしろだって見ないぞ！見ない！見ないって決めたら見ない！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (127, 19, '火星に帰りたい。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「火星に帰りたい。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (128, 19, 'タコメーターってタコの大きさを表示してるんじゃなかったんだ！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「タコメーターってタコの大きさを表示してるんじゃなかったんだ！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (129, 19, 'オドメーターは挙動不審。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「オドメーターは挙動不審。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (130, 19, 'ちゅっ☆');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ちゅっ☆」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (131, 19, 'うけけけけけけけ！あの顔みた？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「うけけけけけけけ！あの顔みた？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (132, 19, 'しなびちゃう。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「しなびちゃう。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (133, 20, '風の強い日は外に出られません。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「風の強い日は外に出られません。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (134, 20, '夏は帽子が欠かせません。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「夏は帽子が欠かせません。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (135, 20, 'エレベーターで女子と一緒になったときは、気を利かせてとにかく降りることにしています。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「エレベーターで女子と一緒になったときは、気を利かせてとにかく降りることにしています。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (136, 20, '愚痴ではありません。感想です。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「愚痴ではありません。感想です。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (137, 20, '奥さんが実家に帰りました。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「奥さんが実家に帰りました。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (138, 20, '子供に「またきてね！」って言われました。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「子供に「またきてね！」って言われました。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (139, 20, '見晴らしの良い席に異動になりました。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「見晴らしの良い席に異動になりました。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (140, 20, '携帯メールを送ったのは2回だけです。宛先は自分です。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「携帯メールを送ったのは2回だけです。宛先は自分です。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (141, 20, '部下には聞けない。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「部下には聞けない。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (142, 20, 'なぜか自分の席のゴミ箱だけ片づけてもらえません。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「なぜか自分の席のゴミ箱だけ片づけてもらえません。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (143, 21, 'バランスへんじゃない？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「バランスへんじゃない？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (144, 21, 'かあああ！！トカサにきた！！！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「かあああ！！トカサにきた！！！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (145, 21, '噛めません。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「噛めません。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (146, 21, 'ガンバレっていうのは簡単だけど、言われたほうとしては本心からそういう言葉を受け入れるのは案外むずかしいよね。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ガンバレっていうのは簡単だけど、言われたほうとしては本心からそういう言葉を受け入れるのは案外むずかしいよね。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (147, 21, 'がむしゃらにやるとたのしい。それがなんでも。たとえば爪切りとか。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「がむしゃらにやるとたのしい。それがなんでも。たとえば爪切りとか。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (148, 21, '寝るのにも体力がいるよ。体力のない人は寝れないんだよ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「寝るのにも体力がいるよ。体力のない人は寝れないんだよ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (149, 21, '早起きは三文の得っていうけど、損得で生きたくないね。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「早起きは三文の得っていうけど、損得で生きたくないね。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (150, 21, 'ぶっ飛んでみたい。腹の底から思いっきり。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ぶっ飛んでみたい。腹の底から思いっきり。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (151, 21, 'オシドリは実は不倫しまくりだ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「オシドリは実は不倫しまくりだ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (152, 21, 'カッコウって頭いいよな。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「カッコウって頭いいよな。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (153, 22, 'アレフガルドが懐かしい。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「アレフガルドが懐かしい。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (154, 22, 'お金が飛んでいくときって羽なんか生えないよ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「お金が飛んでいくときって羽なんか生えないよ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (155, 22, 'ありんこはどんなに高いところから落ちても死なないんだって。挑戦してみる？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ありんこはどんなに高いところから落ちても死なないんだって。挑戦してみる？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (156, 22, 'ぼくらにとって、小事件がありました。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ぼくらにとって、小事件がありました。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (157, 22, 'うけけけけけけけ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「うけけけけけけけ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (158, 22, 'おやつとかたべる？ぼくは人肉が好み。3人くらいペロリだよ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「おやつとかたべる？ぼくは人肉が好み。3人くらいペロリだよ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (159, 22, 'ガッちゃんと勝負してみたい。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ガッちゃんと勝負してみたい。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (160, 22, 'ああ、なんか頭からバリバリと食べたい。小動物とか。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ああ、なんか頭からバリバリと食べたい。小動物とか。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (161, 22, '夕方に目が覚めて朝だか夜だかわからないことってない？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「夕方に目が覚めて朝だか夜だかわからないことってない？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (162, 22, 'テレホーダイ？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「テレホーダイ？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (163, 23, 'おなかすいた！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「おなかすいた！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (164, 23, 'たべるのだいすきだーいすき！あまいのからいのすっぱいぱい！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「たべるのだいすきだーいすき！あまいのからいのすっぱいぱい！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (165, 23, 'カミカミカミカミカミカミカミカミカミカミカミ！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「カミカミカミカミカミカミカミカミカミカミカミ！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (166, 23, 'リンゴはあげない。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「リンゴはあげない。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (167, 23, '「はんぶんずっこ」って言ってわらわれた。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「「はんぶんずっこ」って言ってわらわれた。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (168, 23, 'ぐー。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ぐー。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (169, 23, '腹の虫って、さなだむしのこと？さなだむしがぐーぐーいうの？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「腹の虫って、さなだむしのこと？さなだむしがぐーぐーいうの？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (170, 23, 'ぱくぱくさんにまけないぞ！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ぱくぱくさんにまけないぞ！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (171, 23, '本気出せば光速で移動できますよ。やったことないけど。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「本気出せば光速で移動できますよ。やったことないけど。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (172, 23, 'ムシキングにでた。ヘラクレスつえええ！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ムシキングにでた。ヘラクレスつえええ！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (173, 24, 'ぶーん。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ぶーん。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (174, 24, '⊂二二二（　＾ω＾）二⊃ ぶーん');
		if ($sth->execute(@bind)) {
			push(@msgs, '「⊂二二二（　＾ω＾）二⊃ ぶーん」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (175, 24, 'レーダーにうつらないよ。爆撃できるかも。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「レーダーにうつらないよ。爆撃できるかも。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (176, 24, '赤とんぼの羽を取ってもアブラムシにはならないよな。ぜんぜんちがうし。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「赤とんぼの羽を取ってもアブラムシにはならないよな。ぜんぜんちがうし。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (177, 24, 'おにやんまに負けた。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「おにやんまに負けた。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (178, 24, 'さんまくいたい。炭火で焼いたサンマにだいこんおろしとぽん酢をたらして。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「さんまくいたい。炭火で焼いたサンマにだいこんおろしとぽん酢をたらして。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (179, 24, 'まつたけくいたい。くったことない。うまいの？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「まつたけくいたい。くったことない。うまいの？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (180, 24, '紅葉って枯れてるわけじゃないんだね。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「紅葉って枯れてるわけじゃないんだね。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (181, 24, 'もみじマークってなぜか逆さまに貼ってる人をよく見る。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「もみじマークってなぜか逆さまに貼ってる人をよく見る。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (182, 24, '「子供がのってます」ステッカーのパロディーをよく見る。かなりバカっぽい。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「「子供がのってます」ステッカーのパロディーをよく見る。かなりバカっぽい。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (183, 25, 'おいっち・にー・さんー・しー・にー・にっ・さんー・しー。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「おいっち・にー・さんー・しー・にー・にっ・さんー・しー。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (184, 25, '準備運動でケガした。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「準備運動でケガした。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (185, 25, 'パンチとパンツって似てる。なんとなく。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「パンチとパンツって似てる。なんとなく。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (186, 25, '最近の漫画のキャラって強すぎ。そう簡単に石は割れないと思う。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「最近の漫画のキャラって強すぎ。そう簡単に石は割れないと思う。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (187, 25, 'ひざに水がたまった。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ひざに水がたまった。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (188, 25, '亀のこうら背負って修行したらカメハメ波でるかな？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「亀のこうら背負って修行したらカメハメ波でるかな？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (189, 25, 'ケンシロウとぬけさく先生どっちが強いかな。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ケンシロウとぬけさく先生どっちが強いかな。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (190, 25, 'おみやげに木刀かってきた。もちろん自分用。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「おみやげに木刀かってきた。もちろん自分用。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (191, 25, 'スパゲティーはオリーブオイルと塩こしょうだけでもいける。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「スパゲティーはオリーブオイルと塩こしょうだけでもいける。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (192, 25, '肉と野菜はバランス良く食べよう。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「肉と野菜はバランス良く食べよう。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (193, 26, 'うっふ～ん。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「うっふ～ん。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (194, 26, 'ふつうに考えて弱酸性より中性のほうが肌にやさしいと思う。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ふつうに考えて弱酸性より中性のほうが肌にやさしいと思う。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (195, 26, '首や手首で年がバレる。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「首や手首で年がバレる。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (196, 26, '1円安いものを1000個買うことより、10000円のものを9000円で買う努力をしたほうがいいと思う。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「1円安いものを1000個買うことより、10000円のものを9000円で買う努力をしたほうがいいと思う。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (197, 26, '自分の誕生日は喜ばないのに、他人の誕生日は祝いたがる。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「自分の誕生日は喜ばないのに、他人の誕生日は祝いたがる。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (198, 26, '別腹の存在よりも3段腹のほうが気になる。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「別腹の存在よりも3段腹のほうが気になる。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (199, 26, '本当は大盛りが食べたい。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「本当は大盛りが食べたい。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (200, 26, '自動販売機で缶コーヒーが買えない。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「自動販売機で缶コーヒーが買えない。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (201, 26, 'だるまさんが血まみれ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「だるまさんが血まみれ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (202, 26, '情緒不安定とか自律神経失調症とか鬱とか診断されるとちょっと嬉しい。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「情緒不安定とか自律神経失調症とか鬱とか診断されるとちょっと嬉しい。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (203, 27, 'やられなそうな気がする。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「やられなそうな気がする。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (204, 27, 'なんで足だけなんだろう。手も欲しかった。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「なんで足だけなんだろう。手も欲しかった。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (205, 27, '手なんて飾りですから！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「手なんて飾りですから！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (206, 27, 'ダンプ松本に似てるって言われた。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ダンプ松本に似てるって言われた。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (207, 27, 'ハンバーガーたべたい。ビッグマックさいこー。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ハンバーガーたべたい。ビッグマックさいこー。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (208, 27, 'マクドナルドのピクルスってすごいと思う。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「マクドナルドのピクルスってすごいと思う。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (209, 27, '冷めたフライドポテトでもへいき。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「冷めたフライドポテトでもへいき。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (210, 27, 'マヨネーズを邪道というヤツきらい。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「マヨネーズを邪道というヤツきらい。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (211, 27, '雪道が怖い。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「雪道が怖い。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (212, 27, '転んだら起きられなそう。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「転んだら起きられなそう。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (213, 28, 'やられはせん！やられはせぬぞぉぉぉ！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「やられはせん！やられはせぬぞぉぉぉ！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (214, 28, '「足なんて飾りです」って言われちゃいましたがなにか？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「「足なんて飾りです」って言われちゃいましたがなにか？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (215, 28, '脳天かち割られた。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「脳天かち割られた。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (216, 28, '笑ったらちょっとメガ粒子ふきだしちゃった。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「笑ったらちょっとメガ粒子ふきだしちゃった。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (217, 28, 'ビームは効かないよ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ビームは効かないよ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (218, 28, 'スレッガーなら余裕。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「スレッガーなら余裕。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (219, 28, 'コアブースターは映画版オリジナルだ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「コアブースターは映画版オリジナルだ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (220, 28, '皆が愛してくれた弟ガルマは死んだ。 何故だ！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「皆が愛してくれた弟ガルマは死んだ。 何故だ！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (221, 28, 'ザビ家の栄光！この俺のプライド！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ザビ家の栄光！この俺のプライド！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (222, 28, '圧倒的じゃないか！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「圧倒的じゃないか！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (223, 29, 'ぜんぜん握力がない。ぬいぐるみも持ち上げられない。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ぜんぜん握力がない。ぬいぐるみも持ち上げられない。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (224, 29, '「箸より重いものを持たない」って、箸でご飯をつかんだらもうダメだと思う。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「「箸より重いものを持たない」って、箸でご飯をつかんだらもうダメだと思う。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (225, 29, 'じゃんけんで負け続けた。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「じゃんけんで負け続けた。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (226, 29, 'カニには勝てそう。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「カニには勝てそう。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (227, 29, 'オゾンホールをふさぎに行ってきた。穴なんて見つからなかったよ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「オゾンホールをふさぎに行ってきた。穴なんて見つからなかったよ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (228, 29, 'ニュートリノってなに？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ニュートリノってなに？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (229, 29, '右と左をよく間違えます。助手席にはすわれないかも。カーナビつかって。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「右と左をよく間違えます。助手席にはすわれないかも。カーナビつかって。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (230, 29, 'それを言ったらおしまいな事もあれば、それを言わなきゃはじまらない事もある。でも、じぶんが何を言おうとしてるのかって、よくわからないよね。後になってからわかったりする時もあるけどさ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「それを言ったらおしまいな事もあれば、それを言わなきゃはじまらない事もある。でも、じぶんが何を言おうとしてるのかって、よくわからないよね。後になってからわかったりする時もあるけどさ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (231, 29, 'なんでNTTはカード払いできないんだろう。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「なんでNTTはカード払いできないんだろう。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (232, 29, 'ぜかいま、かなり宇宙食がのみたいなぁ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ぜかいま、かなり宇宙食がのみたいなぁ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (233, 30, 'サイコミュ付けたらエルメスになれたかも？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「サイコミュ付けたらエルメスになれたかも？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (234, 30, 'ララァ載せたかった。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ララァ載せたかった。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (235, 30, 'このスピードを　よけられるか？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「このスピードを　よけられるか？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (236, 30, 'フン、ミサイルの弾幕を張るっていうのはこういう風にやるのよ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「フン、ミサイルの弾幕を張るっていうのはこういう風にやるのよ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (237, 30, 'ん？付属物が付いたぞ。い、いや、もし捉まったなら加速度のショックで気絶しているはずだ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ん？付属物が付いたぞ。い、いや、もし捉まったなら加速度のショックで気絶しているはずだ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (238, 30, 'カニ道楽とまちがわれた。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「カニ道楽とまちがわれた。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (239, 30, '初の量産型モビルアーマーだ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「初の量産型モビルアーマーだ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (240, 30, '普通に考えたらモビルスーツよりモビルアーマーのほうが先に出てくるよね。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「普通に考えたらモビルスーツよりモビルアーマーのほうが先に出てくるよね。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (241, 30, 'ザクレロのデザインはいただけないよね。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ザクレロのデザインはいただけないよね。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (242, 30, '足なんて飾りですから！ってこのとき言っても良かったね。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「足なんて飾りですから！ってこのとき言っても良かったね。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (243, 31, 'にょ～ろ～にょ～ろ～。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「にょ～ろ～にょ～ろ～。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (244, 31, 'いざというときも防御はかんぺきだ！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「いざというときも防御はかんぺきだ！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (245, 31, '寄生虫をもってることがあるので、さわったら必ず手を洗おう！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「寄生虫をもってることがあるので、さわったら必ず手を洗おう！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (246, 31, '乾燥肌です。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「乾燥肌です。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (247, 31, '両刀つかいです。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「両刀つかいです。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (248, 31, '呼び方を統一してください！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「呼び方を統一してください！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (249, 31, 'ツノはわかるけどヤリってどこだろう？');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ツノはわかるけどヤリってどこだろう？」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (250, 31, '右巻きと左巻きがいます。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「右巻きと左巻きがいます。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (251, 31, '紙だって食っちゃいます。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「紙だって食っちゃいます。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (252, 31, '体を切られてもヘッチャラさ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「体を切られてもヘッチャラさ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (253, 32, 'なにがなんだかわかりません。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「なにがなんだかわかりません。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (254, 32, '約束しなきゃ！');
		if ($sth->execute(@bind)) {
			push(@msgs, '「約束しなきゃ！」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (255, 32, '答えなどない。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「答えなどない。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (256, 32, '遊びたい。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「遊びたい。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (257, 32, 'ヤツメウナギの目は普通に2つしかないよ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ヤツメウナギの目は普通に2つしかないよ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (258, 32, '宿題忘れた。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「宿題忘れた。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (259, 32, '今日は朝から夜だった。どんより曇った日本晴れ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「今日は朝から夜だった。どんより曇った日本晴れ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (260, 32, 'ミシンの発明者はミシンを発明したことで服の仕立て屋に襲われた。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「ミシンの発明者はミシンを発明したことで服の仕立て屋に襲われた。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (261, 32, '密組織デストロンの住所がわかった。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「密組織デストロンの住所がわかった。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
		@bind = (262, 32, 'こんとんじょのいこ。');
		if ($sth->execute(@bind)) {
			push(@msgs, '「こんとんじょのいこ。」作成完了');

		} else {
			push(@msgs, "$DBI::err:$DBI::errstr");
		}
	} else {
		push(@msgs, "$DBI::err:$DBI::errstr");
	}



	$dbh->disconnect
		or die($DBI::err . ':' . $DBI::errstr);
	
	push(@msgs, '終了');
}
