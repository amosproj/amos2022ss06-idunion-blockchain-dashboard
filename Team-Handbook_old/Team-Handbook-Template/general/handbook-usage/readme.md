## Advantages

In the AMOS Team 6 our handbook is extensive and keeping it relevant is an important part of everyone's job. The reasons for having our processes described in a handbook are:

1. Reading is much faster than listening.
1. Reading is async, you don't have to interrupt someone or wait for them to become available.
1. On-boarding is easier if you can find all relevant information spelled out.
1. Discussing changes is easier if you can read what the current process is.
1. Communicating change is easier if you can just point to the diff.
1. Everyone can contribute to it by proposing a change via a merge request.

## Flow

1. A (process) problem comes up, frequently in an issue or chat.
1. A proposal is made in a merge request to the handbook.
1. After merging the change is announced by linking to the diff in the MR or commit. 

## Why handbook first

Documenting things in the handbook takes more time initially. You have to think where to make the change, integrate it with the existing content, and possibly add to or refactor the handbook to have a foundation. But it saves time over a longer period and it is essential to scale and adapt our organisation. It is not unlike writing tests for software. Only communicate a (proposed) change via a change to the handbook; don't use a presentation, email, chat message, or another medium to communicate the gist of the change. It might be more convenient to the presenter but it makes it harder for the audience to understand the context and implications for other processes. Handbook first is needed to make sure there is no duplication, the handbook is always up to date, and others are able to contribute.

## Guidelines

Please follow these guidelines and remind others of them.

1. Most guidelines in this handbook are meant to help, and unless stated otherwise, are meant to help more than being absolute rules. Don't be afraid to do something because you don't know the entire handbook, nobody does. Be gentle when reminding people about these guidelines, saying for example, "It is not a problem, but next time please consider the following guideline from the handbook.".

1. If you ask a question and someone answers with a link to the handbook they do this because they want to help by providing more information, and maybe they are proud we have the answer documented. It doesn't mean that you should have read the entire handbook, nobody knows the entire handbook.
1. If you need to discuss with a team member for help please realize that probably the majority of the team also doesn't know, be sure to **document** the answer to radiate this information to the whole team. After the question is answered, discuss where it should be documented and who will do it. You can remind other people of this by asking "Who will document this?"
1. When you discuss something in chat always try to **link** to a URL where relevant, for example, the documentation you have a question about or the page that answered your question. You can remind other people of this by asking "Can you please link?"
1. To change a guideline or process, **suggest an edit** in the form of a merge request.
You can remind other people of this by asking "Can you please send a merge request for the handbook?"
1. Communicate process changes by linking to the **merged diff** (a commit that shows the changes before and after). If you are communicating a change for the purpose of discussion and feedback, it is ok to link to an **unmerged diff**. If  Do not change the process first, and then view the documentation as a lower priority task. Planning to do the documentation later inevitably leads to duplicate work communicating the change and to outdated documentation. You can remind other people of this by asking "Can you please update the handbook first?"
1. Remember, the handbook is not what we hope to do, what we should formally do, or what we did months ago. **It is what we do right now.** So if you want to change a process change the handbook in order to change it. To propose a change to a process make a merge request to change the handbook. Don't use another channel to propose a handbook change (email, chat, etc.).
1. Like everything else, our processes are always in flux. Everything is always in draft, the initial version should be in the handbook, too. If you are proposing a change to the handbook, whenever possible, skip the issue and submit a merge request. Mention the people that affected by the change in the merge request. In many cases, merge requests are easier to collaborate on since you can see the proposed changes.
1. To propose a change a merge request is preferred over an issue description. A merge request allows people to see the context of your change.
1. If something is a limited test to a group of users, add it to the handbook and note as such. Then remove the note once the test is over and every case should use the new process.
1. When communicating something always include a link to the relevant (and up to date) part of the **handbook** instead of including the text in the email/chat/etc. You can remind other people of this by asking "Can you please link to the relevant part of the handbook?"
1. If you copy content please remove it at the origin place and replace it with a link to the new content. Think about the information architecture such that you Don't Repeat Yourself. Duplicate content leads to updating it in the wrong place, keep it [DRY](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself).
1. Make sure to always cross-link items if there are related items (elsewhere in the handbook, in docs, or in issues).
1. The handbook is structured by function and result to ensure every item in it has a clear owner and location in order to keep it up-to-date. Please cross-link liberally to point people to other sections. Avoid unstructured content based on format like FAQ's,lists of links, glossaries, courses, video's, tests, and howto's since these are very hard to keep up to date and are not compatible with organisation per function and result. Instead put the answer, link, definition, course, video, or test in the most relevant place. Use descriptive headers so that people can easily search for content. Please mix different formats in the handbook on the same page, it is engaging to have multiple formats to use and different people prefer different formats. Worry about the organization per function and result, not about how it will look if you embed a different types of content.
1. The handbook is the process. Any section sections with names like 'process', 'policies', 'best practices', or 'standard operating procedures' are an indication of a deeper problem, for example duplication between a prose description of a process and a numbered list description of the same process that should be combined in one description of the process.
1. Use headers liberally. Headers should have normal capitalization (don't use [ALL CAPS](https://en.wikipedia.org/wiki/All_caps) nor [TitleCase](http://www.grammar-monster.com/glossary/title_case.htm)). After a header have one blank line, this is [not required in the standard](http://spec.commonmark.org/0.27/#example-46) but is our convention.

It is each team member's responsibility to ensure the handbook stays current and to verify the content in the handbook is accurate. 

## Make it worthwhile

Another company asked how we managed to work with the handbook because at their company it wasn't working: "There are many occasions where something is documented in the knowledge base, but people don't know about it because they never bothered to read or search. Some people have a strong aversion against what they perceive as a 'wall of text'."

To ensure that people's time is well spend looking at the handbook we should:

1. Keep your handbook pages short and succinct
1. Use present tense and simple words
1. Organize per function so the information architecture is clear
1. Cross-link liberally so I can find relevant other information easily
1. Have clean urls and allow for deeplinking paragraphs
1. Use automatic tables of content
1. Have lots of headers that give the key message
1. Make key words bold
1. When people ask questions link to the handbook instead of giving the answer
1. Test people on their knowledge during onboarding
1. Avoid duplication, instead just link
1. Give real examples
1. Avoid corporate speak, describe things like you're talking to a friend
1. Use lots of numbered lists, unordered lists, and tables
1. Embed video's to consume the content by watching
1. Add drawings and graphics to make it interesting and memorable
1. When someone asks something that isn't there add it to the handbook and respond with a link to the diff
