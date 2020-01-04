# inkscape-kerf-adjuster
<img src="gear.png"/>
creates a kerf-adjusted copy of selected path(s), so that a laser-cut part can be the exact size that was intended

**NOTE: this is a heavy, HEAVY beta.  I'm happy with how it does the path operations, but I haven't been able to get it to consistently respect the kerf setting through transforms,  viewbox scaling, etc**


# Installation
Copy the contents of `src/` to your Inkscape `extensions/` folder.

# Usage
Extensions > Generate from Path > Adjust for Lasercutter Kerf...

# TODO/Limitations

-	currently only works for top-level paths
-	to correctly adjust holes, they should be combined with the thing they are being cut out of.  The easiest way to check this is to add some fill to your path.  The holes should be empty, as with the blue gear above.
-	to use with groups / text, call "Path > Combine" on the offending group/text before running the extension
