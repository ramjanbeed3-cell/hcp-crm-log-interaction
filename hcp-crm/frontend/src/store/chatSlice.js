import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { sendChatMessage } from '../api/client';

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async ({ messages, hcpId }) => {
    const response = await sendChatMessage(messages, hcpId);
    return response;
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [
      {
        role: 'assistant',
        content:
          "Hi, I'm your CRM assistant. Tell me about a visit or call - e.g. " +
          "\"Just met with Dr. Rao, discussed CardioMax dosing, she was positive " +
          "but wants the phase 3 data before prescribing.\"",
      },
    ],
    status: 'idle',
    error: null,
  },
  reducers: {
    addUserMessage(state, action) {
      state.messages.push({ role: 'user', content: action.payload });
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.messages.push({
          role: 'assistant',
          content: action.payload.reply,
          toolCalls: action.payload.tool_calls,
        });
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message;
        state.messages.push({
          role: 'assistant',
          content: 'Sorry, something went wrong reaching the agent.',
        });
      });
  },
});

export const { addUserMessage } = chatSlice.actions;
export default chatSlice.reducer;
