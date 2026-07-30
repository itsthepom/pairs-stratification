# Troubleshooting

Most issues are caused by failing to set the options correctly. Read through the [Options](userif.md#options) section carefully if you are having trouble.

Error messages are displayed in RED. If you get a red message, something has gone badly wrong. Look up the message in the Error Messages table below.

Warning messages are displayed in AMBER. They don't stop you working, but advise you that something isn't quite right. Look up the warning in the Warning Messages table below.

Information messages are in GREEN. They just tell you when an operation has compeleted successfully.

## Error messages
| Message | Cause |
|---------|-------|
| Not a pairs event | The selected tournament is not a pairs event.<br/>This message will also be displayed if there is something wrong with your USEBIO input file. |
| Cannot load webpage template file. | When creating a webpage, this indicates that no webpage template file can been found. Check the file configured in Options exists. |

## Warning messages
| Message | Cause |
|---------|-------|
| Event already stratified.<br/>Re-stratify if you wish | You have loaded up an event from a USEBIO file that already has stratification done on it.<br/>The stratification levels used in the file are also loaded, so going to Stratify Tournament and clicking Stratify will stratify the event in exactly the same way as it was in the loaded file.<br/>You can change the stratification levels and restratify it if you wish. No changes are made to the loaded file. |
| Cannot stratify - Insufficient boards played by some pairs | The event cannot be stratifed because some pairs have played fewer than 18 boards. <br/> You can still print the results showing the per-stratum rankings but the masterpoint scales and awards remain unchanged. |
| Cannot stratify - Insufficient pairs in the lowest stratum. | Insufficient pairs were allocated to the lowest configured stratum to award masterpoints to. For two-winner events you will get this message if there are insufficient pairs in either the N/S or E/W direction.<br/> You can still print the results showing the per-stratum rankings but the masterpoint scales and awards remain unchanged. |

## Message Dialogs


| Message | Cause |
|---------|-------|
| Unable to read member data from Internet - using cached copy.<br/>Member ranks may be out of date. | When the utility starts it reaches out over the Internet to fetch the current rankings from MEMPAD. This message is a warning, indicating that MEMPAD cannot be reached (is your Internet connection OK?).<br/>If the utility has previously contacted MEMPAD it will have cached a copy of the last ranking list obtained from MEMPAD and will use that copy instead.<br/>This means that any recent changes to player rankings will not be used when generating stratified results. |
| Unable to read member data from Internet and no cached copy.<br/>Stratification will not be available. | MEMPAD cannot be reached to obtain the ranking list and there is no cached copy. In this case, no stratification can be performed. This should only occur if your computer has never been able to contact MEMPAD and retrieve the ranking list. |
| Unable to start Help server | Something is preventing the utility from running the local Help server.<br/>Help pages will not be available.<br/>Get your IT person to check nothing is using port TCP/8080. |
| No deal file selected.<br/>Are you sure you wish to create the webpage? | When creating a stand-alone webpage you haven't provided a deal file (.PBN file). No hand records will be generated for the webpage. |
| Different deal date selected.<br/>Are you sure you wish to create the webpage? | The deal file (.PBN file) you selected does not have the same date as the event. You can still use the deal file if you wish - the utility may have got it wrong. This is intended to reduce a common error of picking the wrong deal file. |

## Contact
Please report any issues, bugs or improvement suggestions to <pairsutil@thepom.me.uk>
