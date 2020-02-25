package ch.widmedia.swimmeter.utils.dialogs

import android.app.Dialog
import android.os.Bundle
import androidx.fragment.app.FragmentManager
import ch.widmedia.swimmeter.R
import com.google.android.material.bottomsheet.BottomSheetDialog
import com.google.android.material.bottomsheet.BottomSheetDialogFragment

open class RoundedBottomSheetDialog : BottomSheetDialogFragment() {

    override fun getTheme(): Int = R.style.BottomSheetDialogTheme

    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog = BottomSheetDialog(requireContext(), theme)

    fun show(supportFragmentManager: FragmentManager) {
        show(supportFragmentManager, this.tag)
    }
}