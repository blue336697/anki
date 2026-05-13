# 你应该知道的Git工作流

type: Post
status: Published
date: 2023/10/23
summary: 在看后续内容时，你需要知道的git的简单命令如何进行使用
tags: Git
category: 技术分享

### **在看后续内容时，你需要知道的git的简单命令如何进行使用：[git命令交互式教程](https://learngitbranching.js.org/?locale=zh_CN)、[文本教程](https://backlog.com/git-tutorial/cn/stepup/stepup3_1.html)**

**若使用IDEA自带的maven，则安装路径为：D:\Program Files\JetBrains\IntelliJ IDEA 2024.2.2\plugins\maven\lib\maven3**

**git标准的工作流：**

1. git clone ssh地址 clone到本地
2. git checkout -b xxx 切换至新分支xxx（相当于复制了remote的仓库到本地的xxx分支上修改或者添加本地代码（部署在硬盘的源文件上））这个分支的基础是在你执行此命令的所在的分支所延伸出来的，建议通过在main分支来执行此命令，这么新分支的基础就是main的了

> 如果只想创建新分支不切换，可以使用命令git branch xxxx，切换至该分支则不需要加入-b参数直接使用checkout即可；后续的checkout命令会被switch命令所逐渐替代（2.23起）
> 
1. git diff 查看自己对代码做出的改变，git diff A B可以查看A分支相较于B分支具体有什么区别（在idea控制台中A的代码会显示成红色，B的为绿色），如果后面再加上--stat则会显示出那些文件有区别
2. git add 上传更新后的代码至暂存区，git add . 代表当前目录下所有更新的代码放至暂存区
3. git commit 可以将暂存区里更新后的代码更新到本地git，此时提示因为代码中带有注释，需要去掉注释，但是提交的数据本来就没有注释 怎么解决呢？——>非常简单在git commit文件时指令为git commit -m “文件名”；同理git commit -m "注释，你本次做的有哪些改变"
4. git commit -am "注释"，参数-a在这里代表直接将未提交到暂存器的代码直接提交到本地库中
5. git push origin xxx 将本地的xxxgit分支上传至github上的git

### **如果在写自己的代码过程中发现远端GitLab上代码出现改变：**

1. git checkout main 切换回main分支
2. git pull origin master(main) 将远端修改过的代码再更新到本地
3. git checkout xxx 回到xxx分支
4. git rebase main 我在xxx分支上，先把main移过来，然后根据我的commit来修改成新的内容 （中途可能会出现，rebase conflict ——>手动选择保留哪段代码）
5. git push -f origin xxx 把rebase后并且更新过的代码再push到远端github上 （-f ——>强行）
6. 原项目主人采用pull request 中的 squash and merge 合并所有不同的commit

### **远端完成更新后：**

1. git branch -d xxx 删除本地的git分支
2. git pull origin master 再把远端的最新代码拉至本地

### **当自己的分支上传到远端后，需要合并到某个预发分支时：**

- 首先需要切换到你要合并到的主分支上，git checkout master
- 拉取远端master最新的代码，git pull origin master
- 然后在主分支上使用git merge xxx（你自己的分支），需要保证自己的分支已经上传到远端没有要提交的文件了
- 然后将master分支上的改变push到远端，git push origin master

### **当需要指定合入main分支的文件时**

1. 确保你要合入的分支已经存在并提交你想要合并（修改或者新增）的文件
2. 切换到main分支
3. 使用git checkout 合入分支 – – 具体文件
4. 提交并推送即可

```jsx
`git checkout main`

`git checkout add_invoice_type -- zlop-common/src/main/java/com/br/zlop/common/constant/RmqConsts.java zlop-common/src/main/java/com/br/zlop/common/service/config/ConfigBizQueryService.java zlop-common/src/main/java/com/br/zlop/common/service/mq/RabbitMqListenerSchedule.java zlop-common/src/main/resources/pre/application-common.yml zlop-common/src/main/resources/pre1/application-common.yml zlop-common/src/main/resources/pre3/application-common.yml`

`git commit`

`git push`
```

### **当你想要提交代码，需要更新master分支用来对比时，如果不小心在本地把master分支修改了但又找不到修改的位置，大致有三种解决方法：**

1. 先把master分支修改的东西commit后，在拉取（最不推荐，尽量不要去动master分支的东西）
2. git reset --hard命令进行回退。那么本地你未提交的修改就全部回退了，这个时候就可以成功同步主干代码了。
3. 使用git栈的相关命令完成备份操作，我们先使用git stash将工作区内容进行备份，然后就可以拉取主干分支代码，拉下来后再使用git stash pop命令恢复工作区内容，可能会需要我们手动解决冲突

```jsx
git stash  #备份工作区内容
git pull origin <branch>  #拉取远程分支
git stash pop #恢复工作区内容
```

### **同样当你修改了分支某个文件，想要提交代码时，如果远端分支的这个更新也有更新，此时就会拒绝你的合并，这时解决方法可以复用上面的最后一个**

- 使用git stash现在你的更改放到暂存区里面，相当于把你当前的版本恢复到你更改之前了，这样pull下来的代码百分百不会发生合并错误
- 然后pull拉取最新代码
- 然后git stash pop将暂存区里面你的更改拿出来，这时就可能会有冲突，看你需要什么解决什么就可以了
- 解决完就提交push即可

### **在新建一个分支后，在新分支更改内容是会影响到master分支的，此时应该：**

1. 在新分支上使用 git add. 将改动添加到暂存区
2. 然后使用git commit -m "注释" 进行提交
3. 这样就跟master进行了隔离

### **个人与公司项目的用户名和邮箱进行隔离，此时应该：**

- 在你需要隔离的项目中，使用设置config的两条命令，注意不加--global这个参数，然后进行单独设置就好了

### **当删除分支时，不能checkout在要删除的分支上**

- 先切换到别的分支，在使用命令git branch -d（-D是强制删除）xxx分支名

### **记录一次使用个人电脑配置git的SSH时一直Permission denied，please try again**

- 首先就是平常的现在项目区域（也可直接修改全局的）的用户名和邮箱改为gitlab同款

```jsx
# 去掉--global就是更改项目区域内的配置
git config --global user.name "用户名"
git config --global user.email "用户邮箱"
```

- 然后生成SSH的密钥，这里可能存在多个密钥的情况，所以在生成时要指定生成路径，其中的邮箱要与上一步配置的一致

> Tips：如果是用git bash启动的命令行，那么命令风格是Unix的，如果是win+R启动的则是windows下的命令风格，在写路径时记得区分
> 

```jsx
# 这里写的风格是Unix的
ssh-keygen -t rsa -C "对应仓库邮箱地址@brgroup.com" -f ~/.ssh/密钥文件名
```

- 然后在这个保存密钥的文件夹内创建config，指定你要使用SSH规则，本人就是卡在这一步，一直访问拒绝

```jsx
Host git.100credit.cn    
	User #与第一步的username保持一致    
	Port 22 #可不指定    
	IdentityFile C:\Users\hp\.ssh\xxxx #你要使用的密钥文件名
```

### **给远端分支如何重命名：**

这个的前提是是已经上传了想要改名的那个分支，如果没有上传直接用 git branch -m oldName newName即可

- 第一步同理上面，使用git branch -m oldName newName改本地的分支名
- 使用git push --delete oldName删除你要更改的远程分支
- 使用git push origin newName新建远程分支
- 使用git branch --set-upstream-to origin/newName使本地和远程分支进行关联

### **当本地最近一次commit想要撤销时：**

- 切换到想要撤回的分支git checkout xxx
- 然后使用git reset --soft HEAD^或者**git reset --hard**

> 
> 
- 可以使用git revert HEAD

> 后者命令的区别就是使远端的人也可见了，他会产生一个新的提交，这个提交与你想回到的某个提交一模一样，相当于新瓶装旧酒
> 

### **HEAD——相对移动：**

**众所周知，每个提交记录都会有自己的哈希值，当移动分支时虽然Git很智能，只需要输入前几位就可以，但还是很麻烦。这时就可以使用下面介绍的语法即相对移动，切换你需要移动的分支，移动分支上的提交记录即可**

**HEAD指向的是现在使用中的分支的最后一次更新。通常默认指向master分支的最后一次更新。通过移动HEAD，就可以变更使用的分支。**

使用语法就是**git checkout HEAD~(tilde)和^(caret)**，HEAD后面加上~(tilde）可以指定HEAD之前的提交记录。合并分支会有多个根节点，您可以用^(caret) 来指定使用哪个为根节点。

HEAD^的意思是上一个版本，也可以写成HEAD~1。如果你进行了2次commit，想都撤回，可以使用HEAD~2

![image.png](%E4%BD%A0%E5%BA%94%E8%AF%A5%E7%9F%A5%E9%81%93%E7%9A%84Git%E5%B7%A5%E4%BD%9C%E6%B5%81/image.png)

当然你还可以使用命令来强制将分支移动：git branch -f main HEAD~3，命令会将 main 分支强制指向 HEAD 的第 3 级 parent 提交。或者使用git branch -f main xxx提交点，强制将main精准指向某个提交点

**总结：使用checkout默认移动的HEAD，如果使用branch则移动的是分支；移动的位置可以用相对也可以直接精准指定**

> 疑问：多个分支只有一个HEAD吗？
> 

### **git reset --soft,–hard的区别**

再看这个概念之前，你需要看前面HEAD的概念；还有index暂存区的概念，你所使用的add命令就是将unstaged状态的代码存放到暂存区里，状态变为staged；同时还需要知道working tree，意思是当前的工作目录；所以我们在这里讨论的就是不同mode的区别

git reset<mode><commit>就是将当前所在的分支的HEAD来指向所指定的版本，而标题上的soft和hard则是mode的不同属性，常用的还有mixed

- -soft：使用`-soft`参数将会仅仅重置`HEAD`到制定的版本，不会修改index和working tree，**就是此时你修改的文件还在暂存区中**
- -mixed：使用`-mixed`参数与--soft的不同之处在于，–mixed修改了index，使其与第二个版本匹配。index中给定commit之后的修改被unstaged。**就是将你暂存区里面的修改踢出去，变成没有add的状态**
- -hard：使用`-hard`同时也会修改working tree，也就是当前的工作目录，如果我们执行`git reset --hard HEAD~`，那么最后一次提交的修改，包括本地文件的修改都会被清除，彻底还原到上一次提交的状态且无法找回。所以在执行`reset --hard`之前一定要小心。**就是将你所有的修改记录连根拔除什么都没有**

### **当commit的注释写错时：**

- 使用命令git commit --amend，此时会进入默认[vim编辑器](https://so.csdn.net/so/search?q=vim%E7%BC%96%E8%BE%91%E5%99%A8&spm=1001.2101.3001.7020)，修改注释完毕后保存就好了。

### **禁止自己分支去合并master分支——在自己分支去git merge master的行为：**

- 自己开发的需求当前的代码能够满足，不需要引用别人的最新代码，来给自己的需求提供支持时，严禁在自己的分支去合并master分支的代码，这样会将master分支的提交记录也一并带过来，这样你在提交自己代码到自己的分支就会发现提交记录已经被污染了
- 你所需要的功能在现有master中能够满足就不要用master的代码合并到自己的分支中

### **当你想要删除本地或远端的分支时：**

- 本地删除：使用git branch -d xxx分支名
- 远端删除：使用git push origin --delete xxx分支名

### **当你想要查看本地或者远端分支时：**

- 本地：git branch
- 远程：git branch -r
- 全部：git branch -a，红色的就是远程的

### **当合并代码时出现冲突：**

为什么会出现冲突：当不同的分支都对同一个文件进行编辑，这时你要进行合并就会出现冲突

![image.png](%E4%BD%A0%E5%BA%94%E8%AF%A5%E7%9F%A5%E9%81%93%E7%9A%84Git%E5%B7%A5%E4%BD%9C%E6%B5%81/image%201.png)

当你意识到发生了冲突，这时已经进行了merge或者rebase提示了冲突，如果想要查看详情就可以输入git status来具体查看。随后你有冲突的文件中具体冲突的位置就会被三个标识符包围

- <<<<<<< HEAD和=======之间的内容：是master分支修改的内容（准确来说是HEAD指针指向的分支修改的内容）；
- =======和>>>>>>> new_branch之间的内容：是new_branch分支修改的内容；
- 分割线之外的内容：是两个分支都没有改动的内容

注：修改时需要将这些标识符删除

当你修改完冲突后，你需要将修改的内容进行提交并push等操作；如果你不想解决冲突了，想终止合并，可以输入命令git merge --abort，来回退到合并前的状态

### **当你想要把别的分支的提交记录精准合并到自己的分支时**

使用git cherry-pick xx xx xx，追加提交点即可；那现在出现如果你不知道提交点的哈希值怎么办？——交互式rebase

### **当你想统计项目的行数时**

```jsx
`//全部文件的具体代码行数以及总和`

`git ls-files | xargs wc -l`

`//统计main分支提交人日期在2023-06-12～2023-12-02的提交代码行数`

`git log main --no-merges --since=2023-06-12` `--until=2023-12-02` `--author="haojie.liu"` `--pretty=tformat: --numstat | awk '{ add += $1 ; subs += $2 ; loc += $1 - $2 } END { printf "added lines: %s removed lines : %s total lines: %s\n",add,subs,loc }'`
```

### **交互式rebase**

交互式 rebase 指的是使用带参数 `--interactive` 的 rebase 命令, 简写为 `-i`

如果你在命令后增加了这个选项, Git 会打开一个 UI 界面并列出将要被复制到目标分支的备选提交记录，它还会显示每个提交记录的哈希值和提交说明，提交说明有助于你理解这个提交进行了哪些更改。当界面出现时你只需要做下面这几件事

- 调整提交记录的顺序（通过鼠标拖放来完成）
- 删除你不想要的提交（通过切换 `pick` 的状态来完成，关闭就意味着你不想要这个提交记录）
- 合并提交。 遗憾的是由于某种逻辑的原因，我们的课程不支持此功能，因此我不会详细介绍这个操作。简而言之，它允许你把多个提交记录合并成一个。

随后你就可以编排你的提交记录顺序，例如在一次提交中我们会进行一些修改，基本这个提交可能又会分裂出下一个分支，又会进行修改并提交，那么此时我们想修改之前的提交怎么办？

- 先用 `git rebase -i` 将提交重新排序，然后把我们想要修改的提交记录挪到最前
- 然后用 `git commit --amend` 来进行一些小修改
- 接着再用 `git rebase -i` 来将他们调回原来的顺序
- 最后我们把 main 移到修改的最前端（用你自己喜欢的方法），就大功告成啦！

### **当初出现切换新分支但没没有指定全局pull策略时提示如下**

这是无特殊需求则执行如下设置，意思就是：

- 当`pull.rebase`为`true`时，运行不带选项的命令`git pull`相当于执行`git pull --rebase。`
- 当`pull.rebase`为`false`时，运行不带选项的命令`git pull`不会被改变含义，即不会变基。如果想变基，需要在执行命令时显式地加上选项`-rebase`，即`git pull --rebase`。

```jsx
git config --global --add pull.rebase false
```

![image.png](%E4%BD%A0%E5%BA%94%E8%AF%A5%E7%9F%A5%E9%81%93%E7%9A%84Git%E5%B7%A5%E4%BD%9C%E6%B5%81/image%202.png)

这里有个疑问：就是我在当前分支pull时指定了当前分支的名字，为什么还有提示这个呢，害怕我变基准？

这样做之后会有一个问题：就是相当于我们采用了默认的方式，也就是false，但是这样会让每次的pull如果有新改变执行了merge时都要写merge commit很烦，所以设置为true，相当于我们手动变基为当前分支

### **对于git merge/git rebase的简单学习——等结算这一期需求结束需要删除分支时，试一下**

[两者简单介绍](https://blog.csdn.net/qq_57031340/article/details/126547895)，[两者详解](https://blog.csdn.net/kevinxxw/article/details/123980372)

![image.png](%E4%BD%A0%E5%BA%94%E8%AF%A5%E7%9F%A5%E9%81%93%E7%9A%84Git%E5%B7%A5%E4%BD%9C%E6%B5%81/image%203.png)

### **记录一次error: Your local changes to the following files would be overwritten by checkout:xxx Please commit your changes or stash them before you switch branches.**

请一定每次修改分支时先拉取最新的代码，因为每次可能就会忘记查一下自己在那个分支，如果在master分支，远程上又有更新，此时你不在自己的分支，直接改了本地master，反应过来（如果ctrl+z能够恢复你的修改记录还好，如果没有你只能通过印象或者idea的history来恢复，这对于git相当于修改了文件）就不让你checkout会自己的分支了，很烦

教训：

- 每次更改代码前一定要检查自己所在的分支
- 如果在master或者main上一定要先pull

### **记录一次warning：Line Separators Warning You are about to commot CRLF line separators to the Git repository**

这个警告就是你的提交内容含有不属于当前OS的换行风格

不同OS的换行风格及处理方式，git在读取到不同OS拉下来的代码时会自动处理换行符，在安装git时会有对应三个风格的选项，默认会使用当前安装的OS的风格；

| **OS** | **风格** | **意义** |
| --- | --- | --- |
| Windows-style | CRLF | CRLF表示句尾使用回车换行两个字符(即我们常在Windows编程时使用"\r\n"换行) |
| Unix Style | LF | LF表示表示句尾，只使用换行. |
| Mac Style | CR
 | CR表示只使用回车. |

后续如果要设置则需要输入命令

- 设置为true，添加文件到git仓库时，git将其视为文本文件。他将把crlf变成lf
- 设置为false时，line-endings将不做转换操作。文本文件保持原来的样子。
- 设置为input时，添加文件git仓库石，git把crlf编程lf。当有人Check代码时还是lf方式。因此在window操作系统下，不要使用这个设置。

```jsx
`git config --global core.autocrlf true`

`1) true: x -> LF -> CRLF`

`2) input: x -> LF -> LF`

`3) false: x -> x -> x`
```

### **提交代码或拉去代码时提示：Auto packing the repository in background for optimum performance**

造成原因：git在保存内容时，对加入到暂存区但为及时提交的对象使用到的格式为松散对象 (loose object) 格式，同时会把这些对象统一存储在一个叫 packfile 的二进制文件以节省空间并提高效率。当仓库中有太多的松散对象则就会提示你运行 ' git gc '。

![image.png](%E4%BD%A0%E5%BA%94%E8%AF%A5%E7%9F%A5%E9%81%93%E7%9A%84Git%E5%B7%A5%E4%BD%9C%E6%B5%81/image%204.png)

```jsx
# 查看有多少松散对象
find .git/objects -type f
# 根据当前的配置将对象打包(清理)
git gc
# 不根据当前的配置直接打包(清理)
git gc --prune=now
```

注意：这些对象是用来备份数据的，当时间越久对象越多就会出现这个提示

### **执行git gc后提示如下**

原因：因为在远程分支中，主分支master已经被删除，远程的主分支更换为main，而本地的主分支还是master

解决：同步本地主分支为远程的主分支

```jsx
# 查询本地的主分支
cat .git/refs/remotes/origin/HEAD
# 与远程主分支同步
git remote set-head origin --auto
# 手动指定
git remote set-head origin main
# 执行成功
git gc
```

---

![image.png](%E4%BD%A0%E5%BA%94%E8%AF%A5%E7%9F%A5%E9%81%93%E7%9A%84Git%E5%B7%A5%E4%BD%9C%E6%B5%81/image%205.png)

### **delete tracked branch**

当使用idea删除本地分支时会弹出选项，当选择标题选项时会同步把远程分支也删除，所以这里需要谨慎

### **当想要把某个项目的git信息全部删除，不再有分支信息时**

背景：有些项目只会在本地运行测试，这时如果项目建在了根目录就是git初始化后的目录下，这时新建的项目本身就被git init过的，所以此时想要删除git的相关信息，可以操作两个步骤

- 删除当前目录下的git信息：rm -rf .git
- 删除IDEA与目录的映射关系

![image.png](%E4%BD%A0%E5%BA%94%E8%AF%A5%E7%9F%A5%E9%81%93%E7%9A%84Git%E5%B7%A5%E4%BD%9C%E6%B5%81/image%206.png)

### **There is no tracking information for the current branch.Please specify which branch you want to rebase against.**

背景：这是因为当前分支的默认拉取分支没有指定，即git不知道当前跟踪的版本是什么，我们可以通过两个配置对push和pull的默认行为做约束

你可以通过设置Git的`push.default`和`branch.autoSetupMerge`配置选项来设置Git默认pull或push当前的分支。

- **设置默认push的分支**：你可以使用以下命令来设置`push.default`配置选项为`current`。这意味着当你在一个分支上执行`git push`命令时，Git会将这个分支推送到它的上游分支。

`git config --global push.default` `current`

---

- **设置默认pull的分支**：你可以使用以下命令来设置`branch.autoSetupMerge`配置选项为`always`。这意味着当你创建或克隆一个分支时，Git会自动设置这个分支的上游分支，所以当你在这个分支上执行`git pull`命令时，Git会从这个上游分支拉取更改。

`git config --global branch.autoSetupMerge always`

---

在这两个命令中，`--global`选项意味着这些设置会应用到你的所有Git仓库。如果你只想在当前的仓库中应用这些设置，你可以省略这个选项。

- 请注意，这些设置只影响新的分支。如果你已经有一些分支，你需要手动设置它们的上游分支，你可以使用命令来做这件事。

`git branch --set-upstream-to=origin/<branch> 需要绑定的上游分支名`

---

### **如果换成win本后git提交后的提交描述是乱码则需要设置一下字符集**

`# 与ide的字符集保持一致`

`git config --global i18n.logoutputencoding UTF-8`

`git config --global i18n.commit.encoding UTF-8`

---

以上措施还是没有解决作者的问题，目前的现象是commit或者stash展示提交信息时就会反显出乱码，但是对于远端提交的信息来说是正常的，那么问题原因就出在了本地字符集的匹配

![image.png](%E4%BD%A0%E5%BA%94%E8%AF%A5%E7%9F%A5%E9%81%93%E7%9A%84Git%E5%B7%A5%E4%BD%9C%E6%B5%81/image%207.png)

- 检查ps的字符集是utf-8
- git的提交字符集是utf-8
- windows系统中代码页的字符集是：936（GBK）

> 尝试设置为chcp 65001后，展示回归正常
> 

![image.png](%E4%BD%A0%E5%BA%94%E8%AF%A5%E7%9F%A5%E9%81%93%E7%9A%84Git%E5%B7%A5%E4%BD%9C%E6%B5%81/image%208.png)

但是输入中文后呈现另一种乱码方式，当通过window输入法输入GBK编码后，当前代码页便无法识别

![image.png](%E4%BD%A0%E5%BA%94%E8%AF%A5%E7%9F%A5%E9%81%93%E7%9A%84Git%E5%B7%A5%E4%BD%9C%E6%B5%81/image%209.png)

### **当你想要只合并某些文件时**

假设你有两个分支 `feature-branch` 和 `main`，你只想将 `update.sql` 文件从 `feature-branch` 合并到 `main`。

```jsx
# 切换到 main 分支：
git checkout main
 
# 从 feature-branch 中提取 update.sql 文件：
git checkout feature-branch -- update.sql
 
#提交更改：
git add update.sql
git commit -m "Merged update.sql from feature-branch to main"
```

---

# **git绑定不同域名下的两个仓库**

## 注意：以下操作均在国内项目下！！！！

## 1、git remote

注意：git remote命令不支持添加用户名和邮箱，所以可以直接跳过第一步，直接配置第二部

`# 添加第一个远程仓库（国内一般都存在）`

`git remote add origin http://git.100credit.cn/rd_rdj/rch/tamer.git`

`# 添加第二个远程仓库`

`git remote add dyna-origin http://git.dyna.tech/bdj/rch/tamer.git`

---

添加完没有用户信息

![image.png](%E4%BD%A0%E5%BA%94%E8%AF%A5%E7%9F%A5%E9%81%93%E7%9A%84Git%E5%B7%A5%E4%BD%9C%E6%B5%81/image%2010.png)

## 2、设置.git/config配置

设置搜索：Ignore files and folders

将忽略的.git文件夹展示出来

![image.png](%E4%BD%A0%E5%BA%94%E8%AF%A5%E7%9F%A5%E9%81%93%E7%9A%84Git%E5%B7%A5%E4%BD%9C%E6%B5%81/image%2011.png)

在config下配置

```jsx
[remote "dyna-origin"]
# 项目git
    url = http://git.dyna.tech/bdj/rch/tamer.git
    fetch = +refs/heads/*:refs/remotes/dyna-origin/*
# 自己的海外用户名
    user = tenma.lau
# 自己的海外账号
    email = tenma.lau@dyna.ai
```

---

## 3、修改国内项目的目录

一些通用配置直接从海外项目拷过来并加入后缀名【-dyna】，使其国内的项目是“大而全的”

![image.png](%E4%BD%A0%E5%BA%94%E8%AF%A5%E7%9F%A5%E9%81%93%E7%9A%84Git%E5%B7%A5%E4%BD%9C%E6%B5%81/image%2012.png)

## 4、编写脚本

需要修改的点：

![image.png](%E4%BD%A0%E5%BA%94%E8%AF%A5%E7%9F%A5%E9%81%93%E7%9A%84Git%E5%B7%A5%E4%BD%9C%E6%B5%81/image%2013.png)

project_dir：这个是你项目下存在几个服务就创建几个，如果写了多个，那么

```jsx
current_branch=$(git symbolic-ref --short HEAD)
# Read the user.name and user.email of a specific remote repository
remote_name="dyna-origin"
 
# extract tamer gateway as a variable
project_dir="tamer-gateway"
 
retry_push() {
    local max_attempts=3
    local attempt=1
    local remote=$1
    local branch=$2
 
    git remote update "$remote"
    if git status -uno | grep -q "behind"; then
        echo "Error: Local branch is behind remote. Please pull changes first"
        return 1
    fi
 
    while [ $attempt -le $max_attempts ]; do
        echo "Attempt $attempt of $max_attempts: pushing to $remote..."
        if timeout 180 git push "$remote" "$branch"; then
            return 0
        fi
 
        if git status | grep -q "diverged" || git status | grep -q "behind"; then
            echo "Error: Branch has diverged, please pull and merge manually"
            return 1
        fi
 
        attempt=$((attempt + 1))
        sleep 2
    done
 
    echo "Error: Push failed after $max_attempts attempts"
    return 1
}
 
if [ -n "$(git status --porcelain)" ]; then
    echo "Committing changes..."
    read -p "Enter commit message: " commit_msg
    git add .
    git commit -m "$commit_msg"
fi
 
push_to_dyna() {
    echo "Pushing to dyna-origin..."
    user_name=$(git config --get "remote.$remote_name.user")
    user_email=$(git config --get "remote.$remote_name.email")
 
    temp_dir=$(mktemp -d)
 
    timeout 180 git clone "$(git remote get-url dyna-origin)" "$temp_dir" || {
        echo "Error: Clone timed out"
        rm -rf "$temp_dir"
        return 1
    }
 
    cd "$temp_dir" || {
        echo "Error: Failed to enter temp directory"
        rm -rf "$temp_dir"
        cd "$OLDPWD" || exit
        return 1
    }
 
    if ! git show-ref --verify --quiet "refs/remotes/origin/$current_branch"; then
        echo "Creating new branch: $current_branch"
        git checkout main
        git checkout -b "$current_branch"
    else
        git checkout "$current_branch"
    fi
 
    find . -mindepth 1 -maxdepth 1 -not -name .git -exec rm -rf {} +
 
    cp "$OLDPWD/.gitignore-dyna" .gitignore || {
        echo "Error: .gitignore-dyna not found"
        cd "$OLDPWD" || exit
        rm -rf "$temp_dir"
        return 1
    }
 
    cp "$OLDPWD/pom-dyna.xml" pom.xml || {
        echo "Error: pom-dyna.xml not found"
        cd "$OLDPWD" || exit
        rm -rf "$temp_dir"
        return 1
    }
 
    #------------------------------------------------------------------------从这里开始，有多个project_dir就要写几遍下面的脚本-----------------------------------------------------------
    # create a target directory
    mkdir -p "$project_dir"
 
    # check if the source file exists
    if [ ! -f "$OLDPWD/$project_dir/pom-dyna.xml" ]; then
        echo "Error: Source file $OLDPWD/$project_dir/pom-dyna.xml does not exist"
        cd "$OLDPWD" || exit
        rm -rf "$temp_dir"
        return 1
    fi
 
    # copy the file
    cp "$OLDPWD/$project_dir/pom-dyna.xml" "$project_dir/pom.xml" || {
        echo "Error: Failed to copy pom-dyna.xml"
        cd "$OLDPWD" || exit
        rm -rf "$temp_dir"
        return 1
    }
 
    git add .
    has_changes=false
 
    if git status --porcelain | grep -q '^'; then
        has_changes=true
    fi
 
    if [ -d "$OLDPWD/$project_dir/src/main/resources-dyna" ]; then
        echo "Copying resources to dyan..."
        mkdir -p "$project_dir/src/main/resources"
        cp -r "$OLDPWD/$project_dir/src/main/resources-dyna/." "$project_dir/src/main/resources/"
        git add -f "$project_dir/src/main/resources"
        has_changes=true
    fi
 
    if [ -d "$OLDPWD/$project_dir/src/main/java" ]; then
        echo "Copying java to dyan..."
        mkdir -p "$project_dir/src/main/java"
        cp -r "$OLDPWD/$project_dir/src/main/java/." "$project_dir/src/main/java/"
        git add -f "$project_dir/src/main/java"
        has_changes=true
    fi
 
#------------------------------------------------------------------------从这里结束！！！！！！！！！！！！！！！！！！！！！！-----------------------------------------------------------
 
    if [ "$has_changes" = true ]; then
        git commit -m "chore: deploy files" --author="$user_name <$user_email>"
 
        if ! retry_push origin HEAD; then
            echo "Error: Push to dyna-origin failed after multiple attempts"
            cd "$OLDPWD" || exit
            rm -rf "$temp_dir"
            return 1
        fi
    else
        echo "No changes to commit"
    fi
 
    cd "$OLDPWD" || exit
    rm -rf "$temp_dir"
 
    echo "Successfully pushed to dyna-origin"
    return 0
}
 
target_remote=$1
 
if [ -n "$target_remote" ]; then
    echo "Pushing to $target_remote..."
    if [ "$target_remote" = "dyna-origin" ]; then
        if ! push_to_dyna; then
            echo "Failed to push to dyna-origin"
            exit 1
        fi
    else
        if ! retry_push "$target_remote" "$current_branch"; then
            echo "Failed to push to $target_remote"
            exit 1
        fi
    fi
else
    echo "Pushing to origin..."
    origin_success=false
    dyna_success=false
 
    if retry_push origin "$current_branch"; then
        origin_success=true
    else
        echo "Warning: Failed to push to origin"
        exit 1
    fi
 
    if push_to_dyna; then
        dyna_success=true
    else
        echo "Warning: Failed to push to dyna-origin"
        exit 1
    fi
 
    if ! $origin_success && ! $dyna_success; then
        echo "Error: Failed to push to both repositories"
        exit 1
    fi
 
    if ! $origin_success; then
        echo "Warning: Only pushed to dyna-origin. You may want to retry pushing to origin later."
    elif ! $dyna_success; then
        echo "Warning: Only pushed to origin. You may want to retry pushing to dyna-origin later."
    fi
fi
```

---

## 5、提交代码

由于window下的控制台如果未安装wsl等执行环境是不能执行shell脚本的，所以建议使用git bash进行提交，在项目根目录下执行如下命令，会让其填写commit内容，填写完整个流程结束

`./push.sh`

![image.png](%E4%BD%A0%E5%BA%94%E8%AF%A5%E7%9F%A5%E9%81%93%E7%9A%84Git%E5%B7%A5%E4%BD%9C%E6%B5%81/image%2014.png)

---

## 6、目前存在的问题

### **1-国内外仓库存在代码一样但是坐标不一样的JAR，这里需要全部改成一样的，如不改，则无法则称一份代码，一次修改，一次提交的目的，原因在于坐标不一样，那么引入对应方法或者类的java文件就永远会存在冲突**

## 7、替换引用

```
tech.dyna——》com.br
logtrace-spring-boot-starter——》logtrace-dyna-spring-boot-starter
```

# 不同文件夹绑定不同的git账户（永久）

一、登录

海外Git地址：[https://git.dyna.tech](https://git.dyna.tech/)

email: *用户名***@dyna.ai**

**注意：**首次登录后需要重置密码方可使用

二、 本地git账户配置

本地同时使用国内和海外git账号配置：

**1. 查看默认全局配置**

`git config --global --list`

---

**2. 配置多个git的用户名和邮箱**

注意： 这里git config命令没有带—global，表示这是一个局部的设置，也就是这个用户是当前项目的，而不是全局的

`# 国内`

`git config user.name "xxx"`

`git config user.email "xxx@brgroup.com"`

`# 海外`

`git config user.name "xxx"`

`git config user.email "xxx@dyna.ai"`

---

**3. git-config 配置多用户环境**

1.本地git仓库目录配置建议

![image.png](%E4%BD%A0%E5%BA%94%E8%AF%A5%E7%9F%A5%E9%81%93%E7%9A%84Git%E5%B7%A5%E4%BD%9C%E6%B5%81/image%2015.png)

2. 新增用户gitconfig配置 .gitconfig-dyna, .gitconfig-gitlab 等，其中 .gitconfig-dyna对应海外git账户配置， .gitconfig-gitlab 对应国内git账户配置

![image.png](%E4%BD%A0%E5%BA%94%E8%AF%A5%E7%9F%A5%E9%81%93%E7%9A%84Git%E5%B7%A5%E4%BD%9C%E6%B5%81/image%2016.png)

**.gitconfig**

```jsx
[user]
    name = rain.s
    email = rain.s@global.com
 
[includeIf "gitdir:D:/Repository/GitLab/"]
    path = .gitconfig-gitLab
 
[includeIf "gitdir:D:/Repository/Dyna/"]
    path = .gitconfig-dyna
```

---

**.gitconfig-dyna**

```jsx
[user]
    name = james.li
    email = james.li@dyna.ai
```

---

**.gitconfig-gitlab**

```jsx
[user]
    name = lei.li
    email = lei.li@brgroup.com
```

---

4. 验证

在不同工作目录下如D:/Repository/Dyna/ 下.git的目录下验证 git config user.name 是否为[james.li](http://james.li/)

5. 为每个账户生成密钥,并配置gitlab或dyna

```jsx
`# dyna`

`ssh-keygen -t rsa -b 4096 -C "james.li@dyna.ai"` `-f ~/.ssh/id_rsa_dyna`

`# gitlab`

`ssh-keygen -t rsa -b 4096 -C "lei.li@brgroup.com"` `-f ~/.ssh/id_rsa_dyna`
```

---

6. Maven Setting配置

国内

```jsx
<?xml version="1.0" encoding="UTF-8"?>

<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">
  
  <pluginGroups>
  </pluginGroups>

  <proxies>
  </proxies>

    <!-- 国内 -->
  <servers>
       <server>
        <id>br_server</id>
        <username>dev_deploy_tmp</username>
        <password>v9K!x@3Qw#mT</password>
     </server>

  <server>
        <id>br_server_snapshot</id>
        <username>dev_deploy_tmp</username>
        <password>v9K!x@3Qw#mT</password>
    </server>
    <server>
        <id>br_server_old_snapshot</id>
        <username>dev_deploy_tmp</username>
        <password>v9K!x@3Qw#mT</password>
    </server>

        <server>
        <id>100credit_snapshots</id>
        <username>deployment</username>
        <password>deployment123</password>
    </server>
  </servers>

  <mirrors>
    <mirror>
       <id>br_server_old_snapshot</id>
     <mirrorOf>br_server_old_snapshot</mirrorOf>
       <url>http://192.168.161.221:8081/repository/maven-old-snapshot/</url>
    </mirror>
    <mirror>
       <id>br_server_snapshot</id>
     <mirrorOf>br_server_snapshot</mirrorOf>
       <url>http://192.168.161.221:8081/repository/maven-snapshots/</url>
    </mirror>
    <mirror>
      <id>br_server</id>
      <mirrorOf>*</mirrorOf>
      <url>http://192.168.161.221:8081/repository/maven-public/</url>
    </mirror>
    <mirror>
        <id>aliyun</id>
        <mirrorOf>central</mirrorOf>
        <name>aliyun-public</name>
        <url>https://maven.aliyun.com/repository/public/</url>
    </mirror>
    <mirror>
        <id>aliyun-spring</id>
        <mirrorOf>spring</mirrorOf>
        <name>aliyun-spring</name>
        <url>https://maven.aliyun.com/repository/spring</url>
    </mirror>
  </mirrors>

  <profiles>
    <profile>
       <id>br</id>
          <repositories>
             <repository>
                 <id>br_server</id>
                 <url>http://192.168.161.221:8081/repository/maven-public/</url>
                 <releases>
                    <enabled>true</enabled>
          <updatePolicy>always</updatePolicy>
                 </releases>
          <snapshots>
          <updatePolicy>always</updatePolicy>
                    <enabled>false</enabled>
                </snapshots>
              </repository>
        <repository>
                 <id>br_server_old_snapshot</id>
                 <url>http://192.168.161.221:8081/repository/maven-old-snapshot/</url>
                <releases>
                    <enabled>false</enabled>
                </releases>
                <snapshots>
                    <enabled>true</enabled>
                </snapshots>
              </repository>
              <repository>
                 <id>br_server_snapshot</id>
                 <url>http://192.168.161.221:8081/repository/maven-snapshots/</url>
                <releases>
                    <enabled>false</enabled>
                </releases>
                <snapshots>
                    <enabled>true</enabled>
                </snapshots>
              </repository>
            </repositories>
            <pluginRepositories>
                <pluginRepository>
                    <id>br_server</id>
                    <url>http://192.168.161.221:8081/repository/maven-public/</url>
                    <releases>
                        <enabled>true</enabled>
            <updatePolicy>always</updatePolicy>
                    </releases>
                    <snapshots>
          <updatePolicy>always</updatePolicy>
                        <enabled>true</enabled>
                    </snapshots>
                </pluginRepository>
            </pluginRepositories>
      </profile>
  </profiles>

  <activeProfiles>
      <activeProfile>br</activeProfile>
  </activeProfiles>

  <localRepository>C:\Users\haojie.liu\.m2\repository</localRepository>
</settings>

```

海外：

```jsx
<?xml version="1.0" encoding="UTF-8"?>

<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">
  
  <pluginGroups>
  </pluginGroups>

  <proxies>
  </proxies>

  <servers>
    <!-- 海外 -->
    <server>
        <id>dyna_release</id>
        <username>admin</username>
        <password>QV5%I^MyA8cmw4b0</password>
     </server>
     <server>
        <id>dyna_snapshots</id>
        <username>admin</username>
        <password>QV5%I^MyA8cmw4b0</password>
     </server>
  </servers>

  <mirrors>
    <mirror>
        <id>clojars-daocloud</id>
        <mirrorOf>clojars</mirrorOf>
        <url>http://lbp0200-maven.daoapp.io/repo/</url>
    </mirror>
    <mirror>
        <id>aliyun</id>
        <mirrorOf>central</mirrorOf>
        <name>aliyun-public</name>
        <url>https://maven.aliyun.com/repository/public/</url>
    </mirror>
    <mirror>
        <id>aliyun-spring</id>
        <mirrorOf>spring</mirrorOf>
        <name>aliyun-spring</name>
        <url>https://maven.aliyun.com/repository/spring</url>
    </mirror>
  </mirrors>

  <profiles>
      <profile>
        <id>dyna</id>
        <repositories>
            <repository>
                <id>dyna_release</id>
                <url>https://pypi.dyna.tech/repository/maven-public/</url>
                <releases>
                    <enabled>true</enabled>
                    <updatePolicy>always</updatePolicy>
                </releases>
                <snapshots>
                    <updatePolicy>always</updatePolicy>
                    <enabled>true</enabled>
                </snapshots>
            </repository>
        </repositories>
        <pluginRepositories>
            <pluginRepository>
                <id>nexus</id>
                <url>https://pypi.dyna.tech/repository/maven-public/</url>
                <releases>
                    <enabled>true</enabled>
                    <updatePolicy>always</updatePolicy>
                </releases>
                <snapshots>
                    <updatePolicy>always</updatePolicy>
                    <enabled>true</enabled>
                </snapshots>
            </pluginRepository>
        </pluginRepositories>
    </profile>
  </profiles>

  <activeProfiles>
        <activeProfile>dyna</activeProfile>
  </activeProfiles>

  <localRepository>C:\Users\haojie.liu\.m2\repository_dyna</localRepository>
</settings>

```