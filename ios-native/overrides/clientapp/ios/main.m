/*
 * main.m, part of VCMI engine
 *
 * Authors: listed in file AUTHORS in main folder
 *
 * License: GNU General Public License v2.0 or later
 * Full text of license available in license.txt file, in main folder
 *
 */
#import "startSDL.h"

#import <UIKit/UIKit.h>

#import <objc/runtime.h>

#include <stdlib.h>

static void startSDLManually(int argc, char * argv[])
{
	id<UIApplicationDelegate> appDelegate;
	@autoreleasepool {
		__auto_type sdlAppDelegateClass = NSClassFromString(@"SDLUIKitDelegate");
		NSCAssert(sdlAppDelegateClass != nil, @"SDL AppDelegate class doesn't exist");
		NSCAssert(class_conformsToProtocol(sdlAppDelegateClass, @protocol(UIApplicationDelegate)), @"SDL AppDelegate doesn't conform to UIApplicationDelegate");
		appDelegate = [sdlAppDelegateClass new];
	}
	UIApplication.sharedApplication.delegate = appDelegate;

	int result = startSDL(argc, argv, YES);
	exit(result);
}

int qt_main_wrapper(int argc, char * argv[]);

// Auto-launch direct gameplay for private, asset-inclusive app bundles.
// Public engine-only builds continue to launch the VCMI installer interface.
static BOOL h3MobileHasBundledGameData(void)
{
	NSString * gameDataPath = [NSBundle.mainBundle.bundlePath stringByAppendingPathComponent:@"Data"];
	NSArray<NSString *> * names = [[NSFileManager defaultManager] contentsOfDirectoryAtPath:gameDataPath error:nil];
	BOOL hasBitmap = NO;
	BOOL hasSprite = NO;
	for (NSString * name in names)
	{
		if ([name caseInsensitiveCompare:@"H3Bitmap.lod"] == NSOrderedSame)
			hasBitmap = YES;
		if ([name caseInsensitiveCompare:@"H3Sprite.lod"] == NSOrderedSame)
			hasSprite = YES;
	}
	return hasBitmap && hasSprite;
}

int client_main(int argc, char * argv[])
{
	NSInteger launchType;
	__auto_type envVar = getenv("VCMI_LAUNCH_TYPE");
	if (envVar)
		launchType = envVar[0] == '0' ? 0 : 1;
	else {
		@autoreleasepool {
			// A user-selected launch mode always wins. Otherwise skip the installer
			// only when the app bundle includes the original game data itself.
			id savedMode = [NSUserDefaults.standardUserDefaults objectForKey:@"LaunchType"];
			launchType = savedMode != nil ? [savedMode integerValue] : (h3MobileHasBundledGameData() ? 1 : 0);
		}
	}
	if (launchType == 1)
		return startSDL(argc, argv, NO);

	@autoreleasepool {
		id __block startGameObserver = [NSNotificationCenter.defaultCenter addObserverForName:@"StartGame" object:nil queue:nil usingBlock:^(NSNotification * _Nonnull note) {
			[NSNotificationCenter.defaultCenter removeObserver:startGameObserver];
			startGameObserver = nil;

			NSArray<NSString *> * args = note.userInfo[@"args"];
			const char * newArgv[args.count];
			NSUInteger i = 0;
			for (NSString * obj in args)
				newArgv[i++] = obj.UTF8String;
			startSDLManually(args.count, (char **)(newArgv));
		}];
		return qt_main_wrapper(argc, argv);
	}
}
